# scrapy settings

BOT_NAME = "worker"

SPIDER_MODULES = ["worker.scrapy.spiders"]

# 크롤링 매너
ROBOTSTXT_OBEY = True
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"

# 동시 요청 / 속도 조절
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
AUTOTHROTTLE_DEBUG = False

# 타임아웃 / 재시도
DOWNLOAD_TIMEOUT = 30
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408]

# 쿠키는 필요한 spider에서 custom_settings로 켠다
COOKIES_ENABLED = False

# 캐시는 개발 중에만 사용
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = "httpcache"

ITEM_PIPELINES = {}

# 로그
LOG_ENABLED = True
LOG_LEVEL = "DEBUG"
LOG_STDOUT = True
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Celery worker에서 CrawlerProcess로 실행하므로 종료 시그널은 Celery가 관리한다
TELNETCONSOLE_ENABLED = False

# Scrapy 2.x
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
