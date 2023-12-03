from flask import Flask, render_template, request
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Function to scrape car data from the website
def scrape_cars():
    # Import necessary libraries
    year = []
    name = []
    mileage = []
    rating = []
    review_count = []
    price = []

    # Loop through multiple pages of car listings
    for i in range(1, 11):
        # Construct the URL for each page
        website = 'https://www.cars.com/shopping/results/?page=' + str(i) + '&page_size=20&dealer_id=&list_price_max=&list_price_min=&makes[]=mercedes_benz&maximum_distance=20&mileage_max=&sort=best_match_desc&stock_type=cpo&year_max=&year_min=&zip='

        # Send a request to the website
        response = requests.get(website)

        # Create a BeautifulSoup object
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all car listings on the page
        results = soup.find_all('div', {'class': 'vehicle-card'})

        # Loop through the car listings to extract data
        for result in results:
            # Get the full name from the result
            full_name = result.find('h2').get_text()

            # Initialize variables for year and name
            year_result = 'n/a'
            name_result = full_name

            # Find the first occurrence of four consecutive digits (representing the year)
            for i in range(len(full_name) - 3):
                if full_name[i:i + 4].isdigit():
                    year_result = full_name[i:i + 4]
                    name_result = full_name[:i] + full_name[i + 4:].strip()
                    break

            # Append data to lists (with error handling)
            try:
                name.append(name_result)
            except:
                name.append('n/a')

            try:
                year.append(year_result)
            except:
                year.append('n/a')

            try:
                mileage.append(result.find('div', {'class': 'mileage'}).get_text())
            except:
                mileage.append('n/a')

            try:
                rating.append(result.find('span', {'class': 'sds-rating__count'}).get_text())
            except:
                rating.append('n/a')

            try:
                review_count.append(result.find('span', {'class': 'sds-rating__link'}).get_text().strip('reviews)').strip('('))
            except:
                review_count.append('n/a')

            try:
                price.append(result.find('span', {'class': 'primary-price'}).get_text())
            except:
                price.append('n/a')

    # Create a DataFrame to store the scraped data
    car_dealer = pd.DataFrame({'Year': year, 'Name': name, 'Mileage': mileage, 'Rating': rating,
                               'Review Count': review_count, 'Price': price})

    # Data Cleaning
    # Convert the 'Year' column to integers and handle missing values ('n/a')
    car_dealer['Year'] = pd.to_numeric(car_dealer['Year'], errors='coerce').astype('Int64')

    return car_dealer

app = Flask(__name__)

# Initial scrape when the app starts
car_dealer = scrape_cars()

@app.route('/home')
def index():
    return render_template('index.html', cars=car_dealer.to_dict('records'))

@app.route('/filter', methods=['POST'])
def filter_results():
    min_year = int(request.form['min_year'])
    max_year = int(request.form['max_year'])
    min_price = float(request.form['min_price'])
    max_price = float(request.form['max_price'])
    min_rating = float(request.form['min_rating'])

    # Filter the DataFrame based on user input
    # Convert the 'Rating' column to numeric
    car_dealer['Rating'] = pd.to_numeric(car_dealer['Rating'], errors='coerce')

    filtered_cars = car_dealer[
        (car_dealer['Year'].between(min_year, max_year, inclusive='both')) &
        (car_dealer['Price'].str.replace('[^\d.]', '', regex=True).astype(float).between(min_price, max_price, inclusive='both')) &
        (car_dealer['Rating'] >= min_rating)
    ]

    return render_template('index.html', cars=filtered_cars.to_dict('records'))

@app.route('/start')
def start():
    return render_template('start.html')

@app.route('/seating')
def seating():
    return render_template('seating.html')

if __name__ == '__main__':
    app.run(debug=True)
