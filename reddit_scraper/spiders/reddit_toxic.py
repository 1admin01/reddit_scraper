import scrapy
import json
import requests #OAuth token almak için
from reddit_scraper.items import RedditScraperItem #verilerin şablonu

class RedditToxicSpider(scrapy.Spider):
    name = "reddit_toxic" #spider çağrısı
    allowed_domains = ["reddit.com", "oauth.reddit.com"] #bu domainlere istek atılacak

#Constructor
    def __init__(self, subreddits="all", limit=25, oauth=False, output_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.subreddits = [s.strip() for s in subreddits.split(",")] #virgülle listeye çevir
        self.limit = int(limit) #sayıya
        self.use_oauth = str(oauth).lower() in ("true", "1", "yes") 
        if output_file:
            self.output_file = output_file

        # basit toksik kelime listesi 
        self.toxic_words = {"fuck","bitch","whore","idiot","slut","bastard","asshole"}

        # OAuth token al (eğer oauth=true ise)
        self.access_token = None
        if self.use_oauth:
            cid = self.settings.get("REDDIT_CLIENT_ID")
            secret = self.settings.get("REDDIT_CLIENT_SECRET")
            ua = self.settings.get("USER_AGENT") or "reddit_scraper_app"
            if not cid or not secret:
                raise ValueError("OAuth mode selected but REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET not set in settings.")
            #Reddit’e POST isteği atarak access token alınır
            auth = requests.auth.HTTPBasicAuth(cid, secret)
            data = {"grant_type": "client_credentials"}
            headers = {"User-Agent": ua}
            #Token başka isteklerde Authorization header’ında kullanılacak
            r = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers, timeout=15)
            r.raise_for_status()
            self.access_token = r.json().get("access_token")


    #istek gönder
    def start_requests(self):
        headers = {"User-Agent": self.settings.get("USER_AGENT", "reddit_scraper_app")}
        for sub in self.subreddits:
            if self.use_oauth and self.access_token: #OAuth modundaysa oauth.reddit.com üzerinden token ile istek atılır.
                url = f"https://oauth.reddit.com/r/{sub}/hot?limit={self.limit}"
                headers["Authorization"] = f"bearer {self.access_token}"
            else: # normal Reddit JSON endpoint’inden veri çekilir
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit={self.limit}"
            # Burada meta içine "playwright": True ekledik
        yield scrapy.Request(
            url,
            headers=headers,
            callback=self.parse,
            meta={"subreddit": sub, "headers": headers, "playwright": True}
        )
    def parse(self, response):
        data = json.loads(response.text) #JSON yanıtı Python dict’e çevrilir.
        children = data.get("data", {}).get("children", []) #Gönderi listesi children dizisinden alınır.
        for child in children:
            post = child.get("data", {})
            post_id = post.get("id")  #post verileri iteme doldurulur
            item = RedditScraperItem()
            item["subreddit"] = response.meta.get("subreddit")
            item["post_id"] = post_id
            item["post_title"] = post.get("title")
            item["post_author"] = post.get("author")
            item["post_url"] = f"https://reddit.com{post.get('permalink')}"
            item["post_body"] = post.get("selftext", "")

            yield item #post itemi pipeline a gönderilir csv yazcak

            # yorumları çek
            if post_id: #Post ID’si varsa yorum URL’si oluşturulur.
                if self.use_oauth and self.access_token:
                    comments_url = f"https://oauth.reddit.com/r/{response.meta['subreddit']}/comments/{post_id}?limit=100"
                else:
                    comments_url = f"https://www.reddit.com/r/{response.meta['subreddit']}/comments/{post_id}.json?limit=100"
                headers = response.meta.get("headers", {})
                yield scrapy.Request(comments_url, headers=headers, callback=self.parse_comments, meta={"post_item": item})

    def parse_comments(self, response): #yorumları parse ettik
        post_item = response.meta.get("post_item")
        data = json.loads(response.text)
        # reddit yorum JSON'u bazen liste olarak gelir; ikinci eleman yorumları içerir
        comments = [] #yorum JSON’u bazen liste (post + yorumlar) olarak gelir, bazen dict
        if isinstance(data, list) and len(data) > 1:
            comments = data[1].get("data", {}).get("children", [])
        elif isinstance(data, dict):
            comments = data.get("data", {}).get("children", [])

        for c in comments:
            if c.get("kind") != "t1":  # t1 = comment, t3=post t1 değilse yorum değildir atla
                continue
            cdata = c.get("data", {})
            text = cdata.get("body", "")
            is_toxic = any(w in text.lower() for w in self.toxic_words) #en az biri varsa true

            new_item = RedditScraperItem()
            # post alanlarını koru
            for k in ("subreddit","post_id","post_title","post_author","post_url","post_body"):
                new_item[k] = post_item.get(k)
            new_item["comment_author"] = cdata.get("author")
            new_item["comment_text"] = text
            permalink = cdata.get("permalink") or cdata.get("id")
            new_item["comment_permalink"] = f"https://reddit.com{permalink}" if permalink and permalink.startswith("/") else response.url
            new_item["created_utc"] = cdata.get("created_utc")
            new_item["is_toxic"] = is_toxic

            yield new_item