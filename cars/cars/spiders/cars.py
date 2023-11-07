import scrapy

class CarsSpider(scrapy.Spider):
    name = "cars_spider"
    
    start_urls = ['https://www.cars.com/research/']
    
    def parse(self, response): 
        car_make_pages = ['https://www.cars.com' + x for x in response.css('div#by-make-tab.sds-tabs__section a::attr(href)').getall()]
        # car_make_pages = car_make_pages[10:20]
        
        for car_make in car_make_pages:
            yield scrapy.Request(car_make, callback=self.parse_make_page)
        
    def parse_make_page(self, response):
        
        # response.css('div.sds-card.research-vehicle-card.sds-container--card-actions a.research-vehicle-card-visited-tracking-link::attr(href)').getall()
        car_model_pages = ['https://www.cars.com' + x for x in response.css('div.sds-card.research-vehicle-card.sds-container--card-actions a.research-vehicle-card-visited-tracking-link::attr(href)').getall()]
        
        for model_page in car_model_pages: 
            yield scrapy.Request(model_page, callback=self.parse_model_page)
    
    def parse_model_page(self, response): 
        
        model_details = 'https://www.cars.com' + response.css('div.two-button-container a.sds-button--secondary-fluid.details-button::attr(href)').get()
        
        if model_details: 
            yield response.follow(model_details, callback=self.parse_model_details)
        
    def parse_model_details(self, response):
        
        # make_name = 'hi'
        model_name = response.css('h1.hubcap-type-heading-headline::text').get().replace('\n', '')
        starting_price = response.css('div.msrp.hubcap-type-heading-headline::text').get().replace('\n', '').replace(' ', '')
        year = response.css('div.year::text').get()
        
        yield {
            # "Make": make_name,
            "Model": model_name,
            "Starting Price": starting_price,
            "Year": year
        }