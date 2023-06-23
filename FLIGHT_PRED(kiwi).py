from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time
import sqlite3

from_loc= input("Flying from: ")
to_loc= input("Flying to: ")
departure_date = input("What date (yyyy-mm-dd): ")
arrival_date=input("What date you will arrive (yyyy-mm-dd):")


def search_flight(from_loc, to_loc, departure_date, arrival_date):
    #from_loc = "hyderabad"
    #to_loc = "chennai"
    #departure_date = "2023-04-13"
    #arrival_date = "2023-04-14"
    url = f"https://www.kiwi.com/en/search/results/{from_loc}-india/{to_loc}-india/{departure_date}/no-return"
    print(f"URL: {url}")
    print("The cheapest flights: \n")

    driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()))
    driver.get(url)
    while True:
        # get the height of the page
        last_height = driver.execute_script("return document.body.scrollHeight")

        # scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait for the page to load
        time.sleep(10)

        # get the new height of the page
        new_height = driver.execute_script("return document.body.scrollHeight")

        # check if the page height has stopped changing
        if new_height == last_height:
            break
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    airline_lists = []
    results = soup.find_all('div', {'data-test': re.compile('^ResultCardWrapper')})
    for result in results:
        ariline_name = result.find('img', {'class': re.compile('^CarrierLogo__Styled')})["title"]
        duration = result.find('div', {'data-test': re.compile('^TripDurationBadge')}).text
        stops = result.find('div', {'data-test': re.compile('^StopCountBadge')}).text
        #departure = result.find_all('div', {'class': 'ResultCardItineraryPlacestyled__StyledResultCardItineraryPlace-sc-1ekdizc-5 ghQekA'})[0].text[:5]
        departure = result.find_all('div', {'class': 'ResultCardItineraryPlacestyled__StyledResultCardItineraryPlace-sc-1ekdizc-5 ghQekA'})
        #arrival =departure= result.find_all('div', {'class': 'ResultCardItineraryPlacestyled__StyledResultCardItineraryPlace-sc-1ekdizc-5 ghQekA'})[0].text[:5]
        if departure:
            departure = departure[0].text[:5]
            arrival = departure[0].text[:5]
        else:
            departure = ""
            arrival = ""
        price = result.find('div', {'data-test': 'ResultCardPrice'}).text
        price = re.split('₹', price)[0].strip()

        

        flight = {
            "flight_name": ariline_name,
            "duration": duration,
            "departure_time": departure,
            "arrival_time": arrival,
            "stops": stops,
            "price" : price
        }
        airline_lists.append(flight)

    print(airline_lists)
    cheapest_flight = sorted(airline_lists, key=lambda x: float(re.sub('[^\d.]', '', x['price'])))
    #cheapest_flight = sorted(airline_lists, key=lambda x: float(x['price'].replace(',', '')))
    print(cheapest_flight[0])

    conn = sqlite3.connect('flights1.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS flights
                (flight_name text, flight_duration text, departure_time text, arrival_time text, stops text, price text)''')

    #for flight in airline_lists:
    c.execute('''INSERT INTO flights (flight_name, flight_duration, departure_time, arrival_time, stops, price)
                    VALUES (?, ?, ?, ?, ?, ?)''', (cheapest_flight[0]['flight_name'], cheapest_flight[0]['duration'], cheapest_flight[0]['departure_time'], cheapest_flight[0]['arrival_time'], cheapest_flight[0]['stops'], cheapest_flight[0]['price']))

    conn.commit()
    conn.close()
    
    print("Data inserted into database.")
search_flight(from_loc, to_loc, departure_date, arrival_date)
    
