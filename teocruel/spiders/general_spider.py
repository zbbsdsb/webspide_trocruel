import scrapy
from urllib.parse import urljoin, urlparse
from teocruel.items import TeocruelItem

class GeneralSpider(scrapy.Spider):
    name = 'general_spider'
    
    def __init__(self, url=None, depth=1, max_items=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.allowed_domains = [urlparse(url).netloc] if url else []
        self.depth = int(depth)
        self.max_items = int(max_items)
        self.items_scraped = 0
        self.visited_urls = set()
    
    def parse(self, response):
        if self.items_scraped >= self.max_items:
            return
        
        # 标记当前URL为已访问
        self.visited_urls.add(response.url)
        
        # 创建一个新的Item
        item = TeocruelItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get() or 'No title'
        item['content'] = ' '.join(response.css('p::text').getall()).strip()
        item['status'] = response.status
        item['depth'] = response.meta.get('depth', 0)
        
        self.items_scraped += 1
        yield item
        
        # 如果还有深度剩余，继续爬取链接
        current_depth = response.meta.get('depth', 0)
        if current_depth < self.depth:
            # 提取页面中的所有链接
            for href in response.css('a::attr(href)').getall():
                next_url = urljoin(response.url, href)
                
                # 检查是否是允许的域名，并且没有访问过
                if urlparse(next_url).netloc in self.allowed_domains and next_url not in self.visited_urls:
                    # 添加到已访问URL列表
                    self.visited_urls.add(next_url)
                    
                    # 继续爬取
                    yield response.follow(next_url, callback=self.parse, meta={'depth': current_depth + 1})