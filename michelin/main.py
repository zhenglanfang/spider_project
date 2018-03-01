from scrapy import cmdline

# cmdline.execute('scrapy crawl opentable -o data/lundon.csv'.split())

cmdline.execute('scrapy crawl opentable -o data/newyork2.csv'.split())