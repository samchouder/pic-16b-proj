# __Car Recommendation App__
## Overview
Welcome to the Car Recommendation App! This project is designed to provide users with personalized car recommendations based on their preferences. The application integrates three key technical components: web scraping for real-time market data, building a dynamic website using Flask, and filtering data frames to deliver tailored recommendations. Users start by answering a quiz, receive recommendations, and can explore detailed market information.

## Instructions
1. Clone this repository to your local computer:
'git clone https://github.com/samchouder/pic-16b-proj && cd Car-Recommendation-App'

2. Install the required packages:
'pip install -r requirements.txt'

3. Run the Flask app:
'python app.py' 

Open your web browser and go to http://localhost:5000 to access the Car Recommendation App.

## Project Technical Overview
### Web Scraping
To ensure up-to-date market information, we implemented web scrapers to collect data from Kelley Blue Book (kbb.com/) and from Cars.com (cars.com/). The scrapers extract details on various car models, including price, specifications, and features. The scraped data are then exported to a CSV file for further use in the app.

### Flask Component
The Flask component serves as the backbone of the Car Recommendation App, enabling the creation of a dynamic and interactive user interface. After scraping and exporting data to a CSV file, Flask is used to develop a web application where users can input their preferences through a quiz. The app then leverages Flask sessions to store user inputs, allowing for seamless navigation between different pages. The dynamic nature of Flask facilitates the incorporation of quiz responses into the filtering process, influencing the recommendations presented to users. The routing structure of Flask directs users through various stages of the recommendation process, providing a smooth and intuitive user experience.

### Filtering Data Frames
The filtering component involves the utilization of user preferences obtained through the Flask app to filter the scraped data frame. Functions like numerical_filter and categorical_filter are applied to the data frame, allowing users to narrow down recommendations based on criteria such as price range, seating capacity, fuel type, and drivetrain. Flask sessions efficiently store and retrieve user inputs, ensuring that the recommendations align with the user's specific requirements. This data frame filtering process is crucial for delivering personalized and relevant car recommendations to the end-users.


## Scope, Limitations, Final Discussion
The Car Recommendation App excels in delivering personalized recommendations based on user preferences. However, challenges may arise in maintaining real-time data due to potential changes in the web structure. The app provides a seamless user experience but relies on the accuracy of user inputs. Future enhancements could include additional filtering criteria, visualizations, and expanded market information.

## References and Acknowledgements
Cars.com: https://www.cars.com/

Kelley Blue Book: https://www.kbb.com/

Truecar: https://www.truecar.com/fit-quiz/ 