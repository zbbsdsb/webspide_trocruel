# Teocruel - 多语言网络爬虫

Teocruel是一个功能强大的网络爬虫应用，由ceaserzhao在绵阳中学开发（非官方），提供直观的Web界面，支持多语言操作，允许用户配置爬虫参数、启动爬取任务并可视化结果。

## 功能特点

- **直观的Web界面**：基于Flask开发的用户友好界面
- **多语言支持**：中文、英文、日语、法语、西班牙语
- **灵活的爬虫配置**：
  - 自定义目标URL
  - 控制爬取深度
  - 设置最大爬取数量
  - 任务描述
  - **指定导出目录**：自定义爬取结果的保存路径
- **实时任务状态**：通过AJAX实现任务状态实时更新
- **结果可视化**：以表格或JSON格式展示爬取结果
- **安全可靠**：避免shell注入风险，完善的错误处理

## 技术栈

### 后端
- **Flask**：Python Web框架
- **Flask-Babel**：多语言支持
- **Scrapy**：网络爬虫框架
- **subprocess**：后台任务执行

### 前端
- **HTML5**：页面结构
- **CSS3**：样式设计
- **JavaScript**：交互逻辑
- **AJAX**：异步数据通信

### 数据存储
- **JSON**：任务配置和爬取结果
- **文件系统**：临时文件和日志

## 安装说明

### 1. 克隆项目

```bash
git clone https://github.com/zbbsdab/webspider_teocruel.git
cd webspider_teocruel
```

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Scrapy
pip install scrapy
```

### 3. 配置应用

编辑`app.py`文件，修改应用密钥：

```python
app.secret_key = 'your-secret-key-here'  # 替换为强密钥
```

### 4. 初始化翻译文件

```bash
# 提取翻译字符串
pybabel extract -F babel.cfg -o messages.pot .

# 初始化翻译（已有翻译文件可跳过）
pybabel init -i messages.pot -d translations -l zh
pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l ja
pybabel init -i messages.pot -d translations -l fr
pybabel init -i messages.pot -d translations -l es

# 编译翻译文件
pybabel compile -d translations
```

## 使用指南

### 1. 启动应用

```bash
python app.py
```

应用将在`http://127.0.0.1:5000`启动。

### 2. 配置爬取任务

1. 在浏览器中访问`http://127.0.0.1:5000`
2. 选择您偏好的语言
3. 填写爬取参数：
   - **目标URL**：要爬取的网站URL
   - **爬取深度**：1-10，控制爬取的层级
   - **最大爬取数量**：1-1000，限制爬取的页面数量
   - **导出目录**：结果保存的目录路径（默认：temp）
   - **描述**：任务的简短描述

### 3. 启动爬取任务

点击"开始爬取"按钮，系统将：
1. 验证输入参数
2. 创建指定的导出目录（如果不存在）
3. 生成唯一的任务ID
4. 保存任务配置
5. 在后台启动Scrapy爬虫

### 4. 查看任务状态和结果

任务启动后，页面将显示：
- 任务ID
- 实时状态更新
- 完成后展示爬取结果（表格或JSON格式）

## 多语言支持

Teocruel支持以下语言：

- **中文** (zh)
- **英文** (en)
- **日语** (ja)
- **法语** (fr)
- **西班牙语** (es)

您可以通过页面右上角的语言选择器切换语言。

## 导出目录功能

用户可以在启动爬取任务时指定导出目录，系统将：

1. 验证目录路径的有效性
2. 如果目录不存在，则自动创建
3. 将爬取结果保存到该目录下的`{task_id}_results.json`文件中
4. 在任务状态查询时，从配置文件中读取目录路径

## 项目结构

```
teocruel/
├── app.py                # Flask应用主程序
├── babel.cfg             # Babel配置文件
├── messages.pot          # 翻译模板文件
├── scrapy.cfg            # Scrapy配置文件
├── logs/                 # 日志目录
├── temp/                 # 默认临时文件目录
├── templates/            # HTML模板
│   └── index.html        # 主页面
├── translations/         # 翻译文件
│   ├── zh/               # 中文翻译
│   ├── en/               # 英文翻译
│   ├── ja/               # 日语翻译
│   ├── fr/               # 法语翻译
│   └── es/               # 西班牙语翻译
└── teocruel/             # Scrapy爬虫项目
    ├── __init__.py
    ├── items.py          # 爬取项定义
    ├── middlewares.py    # 中间件
    ├── pipelines.py      # 管道
    ├── settings.py       # 配置
    └── spiders/          # 爬虫
        ├── __init__.py
        └── general_spider.py  # 通用爬虫
```

## 配置说明

### Flask配置

在`app.py`中可以配置：

- `app.secret_key`：应用密钥
- `BABEL_DEFAULT_LOCALE`：默认语言（zh）
- `BABEL_SUPPORTED_LOCALES`：支持的语言列表
- `BABEL_TRANSLATION_DIRECTORIES`：翻译文件目录

### 日志配置

应用使用RotatingFileHandler记录日志：
- 日志文件：`logs/teocruel.log`
- 最大大小：10MB
- 备份数量：5个

## 安全注意事项

1. **应用密钥**：务必在生产环境中使用强密钥
2. **shell注入防护**：使用列表形式的subprocess命令
3. **输入验证**：对所有用户输入进行验证
4. **目录权限**：确保应用对导出目录有读写权限

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：
- Email: your.email@example.com
- GitHub: https://github.com/yourusername/teocruel

---

**版本**：1.1.0
**发布日期**：2025-12-08