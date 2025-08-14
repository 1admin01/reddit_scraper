# USER_AGENT'i kendine göre değiştir (iletişim bilgisi eklemek iyi).
USER_AGENT = "reddit_scraper_app by mercan"
BOT_NAME = "reddit_scraper"
SPIDER_MODULES = ["reddit_scraper.spiders"]
NEWSPIDER_MODULE = "reddit_scraper.spiders"

ROBOTSTXT_OBEY = False #robots.txt’yi yok say
DOWNLOAD_DELAY = 1.0 #Her istek arasında 1 saniye bekleme
CONCURRENT_REQUESTS = 8 #Aynı anda maksimum 8 paralel istek yapar.
#klasör gömme,spider dosyalarını nerede arayacak


ITEM_PIPELINES = {
    "reddit_scraper.pipelines.CSVPipeline": 300, #300, çalışma sırası önçe calışır.
}
#JavaScript render gerekirse Playwright entegrasyonu eklemek için.
# Rate-limit veya JS gerekirse scrapy-playwright kullanabilirsin:
#DOWNLOADER_MIDDLEWARES = {
#   "scrapy_playwright.middleware.ScrapyPlaywrightDownloaderMiddleware": 543,
#}
#TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
#PLAYWRIGHT_BROWSER_TYPE = "chromium"
# Opsiyonel: OAuth bilgilerini buraya koyabilirsin (veya environment variable kullan)
#Reddit’in resmi API’si 
REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""