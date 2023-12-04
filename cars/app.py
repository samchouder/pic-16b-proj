from flask import Flask, render_template, redirect, request, session, flash
from flask_session import Session
import pandas as pd
import re
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to re-read the CSV file
def reread_csv():
    return pd.read_csv('cars/kbb_main.csv')

# Function to filter data based on user input
def categorical_filter(data, column, conditions):
    mask = data[column].isin(conditions)
    filtered_df = data[mask]
    return filtered_df

# Function to filter numerical data based on user input
def numerical_filter(data, column, lower_bound, upper_bound):
    # Make a copy of the original DataFrame
    filtered_df = data.copy()

    # Convert the 'Price' column to numeric values
    filtered_df['Price'] = pd.to_numeric(filtered_df['Price'], errors='coerce')

    # Apply the filter
    filtered_df = filtered_df[(filtered_df[column] >= lower_bound) & (filtered_df[column] <= upper_bound)]
    return filtered_df

# Function to extract numbers from a list of strings
def extract_numbers(string_list):
    numbers = []
    for string in string_list:
        numeric_values = re.findall(r'\d+', string)
        numbers.extend(map(int, numeric_values))
    return numbers

# Function to scrape data from a car market website
def scrape_market_data():
    year = []
    name = []
    mileage = []
    rating = []
    review_count = []
    price = []

    # Loop through multiple pages of car listings
    for i in range(1, 11):
        # Construct the URL for each page
        website = f'https://www.cars.com/shopping/results/?page={i}&page_size=20&dealer_id=&list_price_max=&list_price_min=&makes[]=mercedes_benz&maximum_distance=20&mileage_max=&sort=best_match_desc&stock_type=cpo&year_max=&year_min=&zip='

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
                review_count.append(
                    result.find('span', {'class': 'sds-rating__link'}).get_text().strip('reviews)').strip('('))
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

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the starting page
@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        fuel_values = request.form.getlist('fuel_checkbox')
        session['fuel'] = fuel_values
        return redirect("/seating")
    return render_template('start.html')

# Route for the seating page
@app.route('/seating', methods=['GET', 'POST'])
def seating():
    if request.method == 'POST':
        seat_values = extract_numbers(request.form.getlist('seating_checkbox'))
        min_seats = min(seat_values)
        max_seats = max(seat_values)
        session['min seats'] = min_seats
        session['max seats'] = max_seats
        return redirect('/price')
    return render_template('seating.html')

# Route for the price page
@app.route('/price', methods=['GET', 'POST'])
def price():
    if request.method == 'POST':
        prices = extract_numbers(request.form.getlist('price'))

        if prices:
            session['min price'] = min(prices)
            session['max price'] = max(prices)
            return redirect('/result')
        else:
            flash("Please enter valid price values.")
            return redirect('/price')

    return render_template('price.html')

# Route for the result page
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        min_year = session.get('min year', None)
        max_year = session.get('max year', None)
        min_price = session.get('min price', None)
        max_price = session.get('max price', None)
        min_rating = session.get('min rating', None)

        # Load the data
        df = reread_csv()

        # Apply filters based on user input
        if min_year and max_year:
            df = numerical_filter(df, 'Year', min_year, max_year)
        if min_price and max_price:
            df = numerical_filter(df, 'Price', min_price, max_price)
        if min_rating:
            df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
            df = df[df['Rating'] >= min_rating]

        # Paginate the results
        per_page = 10
        total_pages = -(-len(df) // per_page)  # Ceiling division to calculate total pages
        current_page = session.get('current_page', 1)
        start_index = (current_page - 1) * per_page
        end_index = start_index + per_page
        results_for_page = df.iloc[start_index:end_index]

        return render_template('result.html', cars=results_for_page.to_dict('records'), current_page=current_page,
                               total_pages=total_pages)

    return render_template('result.html', cars=[])

# Add routes for next and back buttons
@app.route('/next', methods=['GET'])
def next_page():
    # Increment the current page in the session
    session['current_page'] = session.get('current_page', 1) + 1
    return redirect('/result')

@app.route('/back', methods=['GET'])
def previous_page():
    # Decrement the current page in the session
    session['current_page'] = max(session.get('current_page', 1) - 1, 1)
    return redirect('/price')

# Route for the market page
@app.route('/market')
def market():
    # Scrape market data
    market_data = scrape_market_data()

    # Your market logic here
    return render_template('market.html', cars=market_data.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)
