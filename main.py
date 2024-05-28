
from scraper import GrabScraper

if __name__ == "__main__":
    location_url = "https://food.grab.com/sg/en/restaurants"
    scraper = GrabScraper(location_url)
    scraper.scrape()
    scraper.save_to_json("restaurants.json")