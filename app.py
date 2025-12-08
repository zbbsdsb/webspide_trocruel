from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_babel import Babel, _
import os
import subprocess
import json
import time
import uuid

# 创建临时目录用于存储爬虫结果
if not os.path.exists('temp'):
    os.makedirs('temp')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 配置日志记录
import logging
from logging.handlers import RotatingFileHandler

# 创建日志目录
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志格式
log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

# 创建文件日志处理器
file_handler = RotatingFileHandler(
    os.path.join('logs', 'teocruel.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))

# 创建控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format))

# 添加日志处理器到应用
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Teocruel application started')

# 配置Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
app.config['BABEL_SUPPORTED_LOCALES'] = ['zh', 'en', 'ja', 'fr', 'es']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# 根据会话选择语言
def get_locale():
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(app, locale_selector=get_locale)

@app.route('/')
def index():
    return render_template('index.html', get_locale=get_locale)

@app.route('/set_language/<lang>')
def set_language(lang):
    app.logger.info(f'User changing language to: {lang}')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = lang
        app.logger.info(f'Language changed successfully to: {lang}')
    else:
        app.logger.warning(f'Attempted to set unsupported language: {lang}')
    return redirect(url_for('index'))

@app.route('/run_spider', methods=['POST'])
def run_spider():
    try:
        url = request.form.get('url')
        depth = request.form.get('depth', 1, type=int)
        max_items = request.form.get('max_items', 100, type=int)
        description = request.form.get('description', '')
        output_dir = request.form.get('output_dir', 'temp')
        
        app.logger.info(f'Received spider request for URL: {url}, depth: {depth}, max_items: {max_items}')
        
        # 验证URL格式
        if not url:
            app.logger.warning('Spider request failed: No URL provided')
            return jsonify({
                'status': 'error',
                'message': _('请提供有效的URL')
            }), 400
        
        # 确保URL包含协议
        if not url.startswith(('http://', 'https://')):
            app.logger.info(f'Adding http:// protocol to URL: {url}')
            url = 'http://' + url
        
        # 验证并创建导出目录
        try:
            # 确保导出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                app.logger.info(f'Created output directory: {output_dir}')
            else:
                app.logger.info(f'Using existing output directory: {output_dir}')
        except OSError as e:
            app.logger.error(f'Failed to create output directory {output_dir}: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': _('创建导出目录失败') + f': {str(e)}'
            }), 500
        
        # 生成唯一的任务ID
        task_id = str(uuid.uuid4())
        
        app.logger.info(f'Generated task ID: {task_id} for URL: {url}')
        
        # 保存任务配置
        task_config = {
            'url': url,
            'depth': depth,
            'max_items': max_items,
            'description': description,
            'output_dir': output_dir,
            'task_id': task_id,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        config_file = os.path.join('temp', f'{task_id}_config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(task_config, f, ensure_ascii=False, indent=2)
        
        app.logger.info(f'Saved task config to: {config_file}')
        
        # 运行Scrapy爬虫
        output_file = os.path.join(output_dir, f'{task_id}_results.json')
        
        # 使用列表形式的命令参数，避免shell注入风险
        spider_cmd = [
            'scrapy', 'crawl', 'general_spider',
            '-a', f'url={url}',
            '-a', f'depth={depth}',
            '-a', f'max_items={max_items}',
            '-o', output_file
        ]
        
        app.logger.info(f'Executing spider command: {spider_cmd}')
        
        # 使用subprocess在后台运行爬虫
        subprocess.Popen(spider_cmd, cwd=os.getcwd())
        
        app.logger.info(f'Spider started successfully for task ID: {task_id}')
        
        # 返回任务ID给前端
        return jsonify({
            'status': 'success',
            'task_id': task_id,
            'message': _('爬虫已开始运行')
        })
    except Exception as e:
        app.logger.error(f'Error running spider: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': _('启动爬虫失败') + f': {str(e)}'
        }), 500

@app.route('/task_status/<task_id>')
def task_status(task_id):
    try:
        # 检查任务状态和结果
        config_file = os.path.join('temp', f'{task_id}_config.json')
        
        # 检查任务是否存在
        if not os.path.exists(config_file):
            return jsonify({
                'status': 'error',
                'message': _('任务不存在或已被删除')
            }), 404
        
        # 从配置文件中读取output_dir
        with open(config_file, 'r', encoding='utf-8') as f:
            task_config = json.load(f)
        
        output_dir = task_config.get('output_dir', 'temp')
        output_file = os.path.join(output_dir, f'{task_id}_results.json')
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                return jsonify({
                    'status': 'completed',
                    'results': results
                })
            except json.JSONDecodeError:
                # 文件存在但不是有效的JSON，可能爬虫正在写入
                return jsonify({
                    'status': 'processing',
                    'message': _('爬虫正在运行中...')
                })
            except Exception as e:
                app.logger.error(f'Error reading results file for task {task_id}: {str(e)}')
                return jsonify({
                    'status': 'error',
                    'message': _('读取爬取结果时发生错误')
                }), 500
        else:
            return jsonify({
                'status': 'processing',
                'message': _('爬虫正在运行中...')
            })
    except Exception as e:
        app.logger.error(f'Error checking task status {task_id}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': _('检查任务状态时发生错误')
        }), 500

if __name__ == '__main__':
    # 创建翻译目录
    if not os.path.exists('translations'):
        os.makedirs('translations')
    app.run(debug=True)