from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def scrape_dynamic_page(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        return soup.title.get_text(strip=True) if soup.title else "No title"
    finally:
        driver.quit()


if __name__ == "__main__":
    url = "https://www.scrapethissite.com/pages/ajax-javascript/"
    title = scrape_dynamic_page(url)
    print("Page title:", title)