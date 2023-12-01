import scrapy

class KBBSpider(scrapy.Spider):
    name = "kbb_spider"
    
    start_urls = ['https://www.cars.com/research/']
    
# goal here is to get to these pages:     
    # https://www.kbb.com/car-finder/?manufacturers=volvo&years=2024-2024
    # by parsing through start url

    def parse(self, response): 
        car_makes = response.css('div#by-make-tab.sds-tabs__section a::attr(href)').getall()
        car_make_pages = ['https://www.kbb.com/car-finder/?manufacturers=' + x[10:].replace('_', '-').replace('/','') + '&years=2023-2024' for x in car_makes]
        
        # shortening to just a few makes
        car_make_pages = car_make_pages[0:1]

        for car_make in car_make_pages:
            if car_make: 
                # print(car_make)
                yield scrapy.Request(car_make, callback=self.parse_make_page)

# goal here is to get to these pages: 
    # https://www.kbb.com/land-rover/defender-110/
    # by parsing through make pages (i.e. https://www.kbb.com/car-finder/?manufacturers=landrover&years=2024-2024)
    
    def parse_make_page(self, response):
        
        # models = response.css('a.css-z66djy.ewtqiv30::attr(href)').getall()
        model_pages = ['https://www.kbb.com' + x for x in response.css('a.css-z66djy.ewtqiv30::attr(href)').getall()]
        
        for model_page in model_pages: 
            yield scrapy.Request(model_page, callback=self.parse_model_page)
    
    
# goal here is to yield specifications for each model
    def parse_model_page(self, response):
        if response.css('div.css-1044rcd.eds0yfe0 h1.css-1l7l3br.e148eed13::text').get() != None:
            name = response.css('div.css-1044rcd.eds0yfe0 h1.css-1l7l3br.e148eed13::text').get()
        else: 
            name = "N/A"
            
        reviews = response.css('div.css-1c7qqqr::text').getall()
        if len(reviews) == 0: 
            expert_review = "N/A"
            consumer_review = "N/A"
        elif len(reviews) == 1: 
            if response.css('div.css-1p1bpqh > div.css-hryd08::text').get() == 'Consumer':
                expert_review = "N/A"
                consumer_review = reviews[0]
            else:
                expert_review = reviews[0]
                consumer_review = "N/A"
        else: 
            expert_review = reviews[0]
            consumer_review = reviews[1]
        
        
        yield {
            "Name": name,
            "Expert Review": expert_review, 
            "Consumer Review": consumer_review
        }
        
        # CAR NAME
        # overview > div.css-13ecko2.eds0yfe0 > div.css-1oa9s8j.e1ngkdb71 > div > div > div.css-1044rcd.eds0yfe0 > h1
        
        # REVIEWS --> response.css('div.css-1c7qqqr::text').getall()
        # expert review
            # #overview > div.css-13ecko2.eds0yfe0 > div.css-1oa9s8j.e1ngkdb71 > div > div > div.css-1044rcd.eds0yfe0 > div > div > div:nth-child(1) > div > div > div.css-1c7qqqr
        # consumer review 
        
        # SPECIFICATIONS --> #specs > div > div
        
        # response.css('div.css-tpw6mp.e1ma5l2g3::text').getall() --> for the first four highlighted specs; can't distinguish between them though
        
        # fuel economy 
            # specs > div > div > div.css-1oi9yv0.eds0yfe0 > div > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(1) > div.css-1d3w5wq.e181er9y1 > div > div.css-1xdhyk6.e1ma5l2g0 > div > div
            
        # fuel type 
            # specs > div > div > div.css-1oi9yv0.eds0yfe0 > div > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div.css-1d3w5wq.e181er9y1 > div > div.css-1xdhyk6.e1ma5l2g0 > div > div
        

        # vehicle_card_0 > div.css-ssaa7u.ewtqiv32 > div.css-1u90y2t.e19qstch16 > div > div > a
        # response.css('vehicle_card_0 > div.css-ssaa7u.ewtqiv32 > div.css-1u90y2t.e19qstch16 > div > div > a::attr(href)').get()
        # response.css('#vehicle_card_0 > div.css-ssaa7u.ewtqiv32 > div.css-1frey1d.e19qstch16 > div > div
        
        # css-zk8aw5 e19qstch11 <-- each href for the listed models have this div class
        # css-z66djy ewtqiv30 
        
        
        
    