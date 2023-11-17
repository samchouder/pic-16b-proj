import scrapy

class CarsSpider(scrapy.Spider):
    name = "cars_spider"
    
    start_urls = ['https://www.cars.com/research/']
    
    def parse(self, response): 
        car_make_pages = ['https://www.cars.com' + x for x in response.css('div#by-make-tab.sds-tabs__section a::attr(href)').getall()]
        # car_make_pages = car_make_pages[12:25] #this has to be more than 1 url
        
        for car_make in car_make_pages:
            yield scrapy.Request(car_make, callback=self.parse_make_page)
        
    def parse_make_page(self, response):
        
        car_model_pages = ['https://www.cars.com' + x for x in response.css('div.sds-card.research-vehicle-card.sds-container--card-actions a.research-vehicle-card-visited-tracking-link::attr(href)').getall()]
        
        for model_page in car_model_pages: 
            yield scrapy.Request(model_page, callback=self.parse_model_page)
    
    def parse_model_page(self, response): 
        
        model_details = 'https://www.cars.com' + response.css('div.two-button-container a.sds-button--secondary-fluid.details-button::attr(href)').get()
        
        if model_details: 
            yield response.follow(model_details, callback=self.parse_model_details)
        
    def parse_model_details(self, response):
        
        make = response.css('ul.sds-breadcrumb.sds-breadcrumb--mobile-custom > li:nth-child(3) > a::text').get()
        model = make + " " + response.css('ul.sds-breadcrumb.sds-breadcrumb--mobile-custom > li:nth-child(4) > a::text').get()
        year = response.css('ul.sds-breadcrumb.sds-breadcrumb--mobile-custom > li:nth-child(6)::text').get()

        yield {
            "Make": make,
            "Model": model,
            # "Starting Price": starting_price, 
            "Year": year
            # "Seating Capacity": seats, 
            # # gas, hybrid, electric (?)
            # "Engine": engine_type, 
            # "Fuel Efficiency": mpg, 
        }

#         model_name = response.css('h1.hubcap-type-heading-headline::text').get().replace('\n', '')
#         starting_price = response.css('div.msrp.hubcap-type-heading-headline::text').get().replace('\n', '').replace(' ', '')
#         year = response.css('div.year::text').get()
        
#         yield {
#             "Model": model_name,
#             "Starting Price": starting_price,
#             "Year": year
#         }
        

# response.css('h1.spark-heading-1.sds-page-section__title::text').get() --> to get make name from make page

# to get the name of the make on the MODEL PAGE (i.e. 'https://www.cars.com/research/honda-accord/')
    # ae-skip-to-content > div.research-make-model-page > section.sds-page-section.sds-page-section--header > header > nav > ul > li:nth-child(3) > a
    # css selector 
        # response.css('div.research-make-model-page > section.sds-page-section.sds-page-section--header > header > nav > ul > li:nth-child(3) > a::text').get()

        
# get MAKE NAME on MODEL'S MORE DETAILS page
    # new-cars-model-header-wrapper > header > nav > ul > li:nth-child(3) > a
    
    # response.css('ul.sds-breadcrumb.sds-breadcrumb--mobile-custom > li:nth-child(3) > a::text').get()
    
# get MODEL NAME on MODEL'S MORE DETAILS page 
    # response.css('ul.sds-breadcrumb.sds-breadcrumb--mobile-custom > li:nth-child(4) > a::text').get()

# get MODEL YEAR on MODEL'S MORE DETAILS page
    # response.css('ul.sds-breadcrumb.sds-breadcrumb--mobile-custom > li:nth-child(6)::text').get()
    
# get STARTING PRICE on MODEL's MORE DETAILS PAGE
    # 
    
# get SEATING CAPACITY on MODEL'S MORE DETAILS page
    # panel-127 > div:nth-child(4) > div.key-spec-value
    
