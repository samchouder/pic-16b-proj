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
def reading_csv():
    df = pd.read_csv('cars/kbb_main.csv')
    
    # converting Price column to numerical data
    df['Price'] = df['Price'].str.replace('$','')
    df['Price'] = pd.to_numeric(df['Price'].str.replace(',', ''), errors='coerce')
    return df

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
    # filtered_df['Price'] = pd.to_numeric(filtered_df['Price'], errors='coerce')

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
def start():
    return render_template('start.html')

# Route for the fueling page
@app.route('/fuel', methods=['GET', 'POST'])
def fuel():
    if request.method == 'POST':
        fuel_values = request.form.getlist('fuel_checkbox')
        session['fuel'] = fuel_values

        print("Fuel Type found " + str(session['fuel']))

        return redirect("/seating")
    return render_template('fuel.html')

# Route for the seating page
@app.route('/seating', methods=['GET', 'POST'])
def seating():
    if request.method == 'POST':
        seat_values = extract_numbers(request.form.getlist('seating_checkbox'))
        min_seats = min(seat_values)
        max_seats = max(seat_values)
        session['min seats'] = min_seats
        session['max seats'] = max_seats

        print("Seating Capacity Found " + str(session['min seats']) + " " + str(session['max seats']))

        return redirect('/price')
    return render_template('seating.html')


# Route for the price page
@app.route('/price', methods=['GET', 'POST'])
def price():
    if request.method == 'POST':
        # prices = extract_numbers(request.form.getlist('price_input'))
        min_price = int(request.form.get('min_price'))
        max_price = int(request.form.get('max_price'))
        print("Price Range Found " + str(min_price) + " " + str(max_price))

        if min_price and max_price:
            # session['min price'] = int(prices[0])
            # session['max price'] = int(prices[1])
            session['min price'] = min_price
            session['max price'] = max_price
            print(session['min price'] + session['max price'])
            return redirect('/result')
        else:
            flash("Please enter valid price values.")
            return redirect('/price')

    return render_template('price.html')


# Route for the drivetrain page
@app.route('/drivetrain', methods=['GET', 'POST'])
def drivetrain():
    if request.method == 'POST':
        drivetrain_values = request.form.getlist('drivetrain_checkbox')
        session['drivetrain'] = drivetrain_values
        return redirect('/results')
    
    return render_template('drivetrain.html')


# Route for the result page
@app.route('/result')
def result():
    min_price = session.get('min price', None)
    max_price = session.get('max price', None)
    min_seats = session.get('min seats', None)
    max_seats = session.get('max seats', None)
    fuel = session.get('fuel', None)

    print("Flask Session Data: ")
    print(min_price)
    print(max_price)
    print(min_seats)
    print(max_seats)
    print(fuel)

    # Load the data
    df = reading_csv()
    print(df.head())
    
    # Apply filters based on user input
    if min_price and max_price:
        df = numerical_filter(df, 'Price', min_price, max_price)
        print(df.head())
    if min_seats and max_seats: 
        df = numerical_filter(df, 'Seating Capacity', min_seats, max_seats)
        print(df.head())
    if fuel:
        df = categorical_filter(df, 'Fuel Type', fuel)
        print(df.head())
    # if min_rating:
    #     df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    #     df = df[df['Rating'] >= min_rating]

    # Paginate the results
    per_page = 25
    total_pages = -(-len(df) // per_page)  # Ceiling division to calculate total pages
    current_page = session.get('current_page', 1)
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page
    results_for_page = df.iloc[start_index:end_index]

    return render_template('result.html', cars=results_for_page.to_dict('records'), current_page=current_page, total_pages=total_pages)

# Route for the market page
@app.route('/market')
def market():
    # Scrape market data
    market_data = scrape_market_data()
    # Your market logic here
    return render_template('market.html', cars=market_data.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)
