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

        for car_make in car_make_pages:
            if car_make: 
                yield scrapy.Request(car_make, callback=self.parse_make_page)

# goal here is to get to these pages: 
    # https://www.kbb.com/land-rover/defender-110/
    # by parsing through make pages (i.e. https://www.kbb.com/car-finder/?manufacturers=landrover&years=2024-2024)
    
    def parse_make_page(self, response):
        
        model_pages = ['https://www.kbb.com' + x for x in response.css('a.css-z66djy.ewtqiv30::attr(href)').getall()]
        
        for model_page in model_pages: 
            yield scrapy.Request(model_page, callback=self.parse_model_page)
    
    
# goal here is to yield specifications for each model
    def parse_model_page(self, response):
        # name
        if response.css('div.css-1044rcd.eds0yfe0 h1.css-1l7l3br.e148eed13::text').get() != None:
            name = response.css('div.css-1044rcd.eds0yfe0 h1.css-1l7l3br.e148eed13::text').get()
        else: 
            name = response.css('div.css-1044rcd.eds0yfe0 h1.css-54ra7u.e148eed13::text').get()
 
        table = response.css('table.css-1b8ug1h.e1d7xkd00 > tbody.css-1dfwth1.e1d7xkd05')
        rows = table.css('tr')
        
        
        price = rows[0].css('td.css-d4cyqu.e1d7xkd04 > span::text').get()
        fuel_type = rows[4].css('td.css-d4cyqu.e1d7xkd04 > div::text').get()
        fuel_econ = rows[3].css('td.css-d4cyqu.e1d7xkd04 > div::text').get()
        seating_capacity = rows[7].css('td.css-d4cyqu.e1d7xkd04::text').get()
        
        kbb_rating = rows[1].css('td.css-d4cyqu.e1d7xkd04 > div > span::text').get()
        if kbb_rating == None:
            kbb_rating = "N/A"
        consumer_rating = rows[2].css('td.css-d4cyqu.e1d7xkd04 > div > span::text').get()
        if consumer_rating == None:
            consumer_rating = "N/A"
        safety_rating = rows[6].css('td.css-d4cyqu.e1d7xkd04 > div > span::text').get()
        if safety_rating == None: 
            safety_rating = "N/A"
            
        horsepower = rows[9].css('td.css-d4cyqu.e1d7xkd04 > div::text').get()
        engine = rows[10].css('td.css-d4cyqu.e1d7xkd04 > div::text').get()
        wheeldrive = rows[11].css('td.css-d4cyqu.e1d7xkd04 > div::text').get()
        
        yield {
            "Name": name,
            "Price": price, 
            "Fuel Type": fuel_type, 
            "Fuel Economy": fuel_econ, 
            "Seating Capacity": seating_capacity, 
            "Engine": engine,
            "Drivetrain": wheeldrive, 
            "Horsepower": horsepower,
            "KBB Rating": kbb_rating, 
            "Consumer Rating": consumer_rating,
            "Safety Rating": safety_rating
        }