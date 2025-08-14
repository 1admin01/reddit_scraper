import scrapy
#veri şablonu (data container)
class RedditScraperItem(scrapy.Item): #Reddit’ten çekeceğim veriler şu alanlardan oluşacak
    subreddit = scrapy.Field() #belirli bir konu veya topluluğa ait bölüm
    post_id = scrapy.Field()
    post_title = scrapy.Field()
    post_author = scrapy.Field()
    post_url = scrapy.Field()
    post_body = scrapy.Field()
    comment_author = scrapy.Field()
    comment_text = scrapy.Field()
    comment_permalink = scrapy.Field() #direktlink
    created_utc = scrapy.Field() #Unix zaman damgası
    is_toxic = scrapy.Field()