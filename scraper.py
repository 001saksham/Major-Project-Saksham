import concurrent.futures
import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from restaurant import Restaurant
import json

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
logging.basicConfig(level=logging.INFO)


class GrabScraper:
    def __init__(self, location_url, target_count=200):
        self.location_url = location_url
        self.target_count = target_count
        self.restaurants = []

    def fetch_page(self, url):
        driver.get(url)
        time.sleep(5)
        return BeautifulSoup(driver.page_source, 'html.parser')

    def parse_page(self, page):
        for restaurant_div in page.find_all('div', class_='RestaurantListCol___1FZ8V'):

            image_tag = restaurant_div.find('img', class_='realImage___2TyNE')
            image_link = image_tag['src'] if image_tag and 'src' in image_tag.attrs else 'Unable to fetch Image'

            name = restaurant_div.find('p', class_='name___2epcT')
            name = name.text.strip() if name else ''

            cuisine = restaurant_div.find('div', class_='basicInfoRow___UZM8d cuisine___T2tCh')
            cuisine = cuisine.text.strip() if cuisine else ''

            rating_div = restaurant_div.find('div', class_='numbersChild___2qKMV')
            rating = rating_div.text.strip() if rating_div else ''
            if len(rating) >= 4:
                rating = "No Rating"

            est_delivery_time_div = restaurant_div.find('div', class_='basicInfoRow___UZM8d numbers___2xZGn').text.strip()
            est_delivery_time, duration = est_delivery_time_div.split('  •  ')

            promotion_offers_span = restaurant_div.find('span', class_='discountText___GQCkj')
            promotion_offers = promotion_offers_span.text.strip() if promotion_offers_span else 'No promotion offers'
            if len(promotion_offers) == 0:
                promotion_offers = 'Null'


            restaurant = Restaurant(
                image_link, name, cuisine, rating, est_delivery_time, duration,
                promotion_offers
            )
            self.restaurants.append(restaurant)

        logging.info(f"Found {len(self.restaurants)} restaurants")

    def scroll_and_collect(self):
        while len(self.restaurants) < self.target_count:
            self.parse_page(BeautifulSoup(driver.page_source, 'html.parser'))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait for new content to load
            if len(self.restaurants) >= self.target_count:
                break

    def scrape(self):
        logging.info('Fetching page ... ')
        self.fetch_page(self.location_url)
        logging.info('Page fetched successfully')
        logging.info('Scrolling and collecting data ... ')
        self.scroll_and_collect()
        logging.info('Data collection completed')

    def save_to_json(self, file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            json_data = [restaurant.to_dict() for restaurant in self.restaurants]
            json.dump(json_data, f, ensure_ascii=False, indent=4)


def scrape_location(location_url):
    scraper = GrabScraper(location_url)
    scraper.scrape()
    return scraper.restaurants


if __name__ == "__main__":
    location_urls = [
        "https://food.grab.com/sg/en/restaurants"
    ]

    all_restaurants = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(scrape_location, url) for url in location_urls]
        for future in concurrent.futures.as_completed(futures):
            all_restaurants.extend(future.result())

    unique_restaurants = {restaurant.name: restaurant for restaurant in all_restaurants}.values()

    scraper = GrabScraper("")
    scraper.restaurants = list(unique_restaurants)
    scraper.save_to_json("restaurants.json")
