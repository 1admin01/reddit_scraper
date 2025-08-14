import csv
#toplanan verileri CSV dosyasına yazmak.
class CSVPipeline:
    def open_spider(self, spider): #CSV dosyasını açmak.
        fname = getattr(spider, "output_file", spider.settings.get("OUTPUT_FILE", "reddit_comments.csv"))
        self.file = open(fname, "w", newline="", encoding="utf-8")
        self.fieldnames = [ #itemsdeki başlıklar
            "subreddit","post_id","post_title","post_author","post_url","post_body",
            "comment_author","comment_text","comment_permalink","created_utc","is_toxic"
        ]
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames) #direkt CSV’ye yazabilmemizi sağlar.sözlük formatındaki verileri, fieldnames ile hangi sütunlara hangi verilerin gideceğini belirtiyoruz.
        self.writer.writeheader() #csv nin başlık satırını yazar


#Her item yakalandığında Scrapy tarafından otomatik çağrılır.
    def process_item(self, item, spider):
        row = {k: item.get(k, "") for k in self.fieldnames}
        self.writer.writerow(row)
        return item

    def close_spider(self, spider): #dosya bozulmalarını önler.
        self.file.close()