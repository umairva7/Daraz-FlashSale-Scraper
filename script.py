from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

# Setup the WebDriver
path = 'C:/Users/mari7/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe'
service = Service(path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Navigate to the page
driver.get(
    'https://pages.daraz.pk/wow/gcp/route/daraz/pk/upr/router?hybrid=1&data_prefetch=true&prefetch_replace=1&at_iframe=1&wh_pid=%2Flazada%2Fchannel%2Fpk%2Fflashsale%2F7cdarZ6wBa&hide_h5_title=true&lzd_navbar_hidden=true&disable_pull_refresh=true&skuIds=449317740%2C166492518%2C460240288%2C477241078%2C488424967%2C155100053%2C433738803&spm=a2a0e.tm80335159.FlashSale.d_shopMore')

driver.maximize_window()

# Load more products by clicking the "Load More" button
for i in range(1):
    try:
        # Wait for the "Load More" button to be clickable
        load_Button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='button J_LoadMoreButton']"))
        )
        load_Button.click()
        # Adding a short wait to ensure that the products load after clicking
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="sale-title"]'))
        )
    except TimeoutException:
        print(f"Load more button not found or no more products to load at iteration {i}.")
        break

# Get product links
product_links = driver.find_elements(By.XPATH, "//div[@class='item-list-content clearfix']/div/a")
print(len(product_links))
href_list = []
titles = []
original_prices = []
sale_prices = []
store_names = []
brands = []
ratings = []
URLs = []

# Print the href attributes of each link
for i, link in enumerate(product_links):
    href_list.append(link.get_attribute('href'))

# Visit each product page and scrape store names
for i in range(len(href_list)-15):
    try:
        product_url = href_list[i]
        driver.get(product_url)

        # Re-find the element on the new page
        store_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='seller-name__detail']/a"))
        )
        product_name = driver.find_element(By.XPATH, "//h1")
        sale_price = driver.find_element(By.XPATH, '//div[@class="pdp-product-price"]/span')
        org_price = driver.find_element(By.XPATH, '//div[@class="origin-block"]/span')
        reviews = driver.find_element(By.XPATH, '//div[@class="pdp-review-summary"]/a')

        # Handle cases where specification elements might not be present
        try:
            brand = driver.find_element(By.XPATH, '//div[@class="pdp-product-brand"]/a[@class="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-product-brand__brand-link"]')
            brands.append(brand.text)
        except NoSuchElementException:
            brands.append("N/A")  # If no brand is found, append "N/A"

        org_price = org_price.text.replace('Rs.', '')
        sale_price = sale_price.text.replace('Rs.', '')
        reviews = reviews.text.replace('Ratings', '')

        URLs.append(product_url)
        ratings.append(reviews)
        titles.append(product_name.text)
        original_prices.append(org_price)
        sale_prices.append(sale_price)
        store_names.append(store_name_element.text)

    except (StaleElementReferenceException, TimeoutException, NoSuchElementException) as e:
        print(f"Exception for product {i}: {e}, skipping")
        titles.append("N/A")
        original_prices.append("N/A")
        sale_prices.append("N/A")
        store_names.append("N/A")
        brands.append("N/A")

    finally:
        # Navigate back to the main page and re-fetch product links
        driver.back()
        product_links = driver.find_elements(By.XPATH, "//div[@class='item-list-content clearfix']/div/a")

# Quit the driver
driver.quit()

# Save to CSV
data = {
    'Product Name': titles,
    'Original Price': original_prices,
    'Sale Price': sale_prices,
    'Store Name': store_names,
    'Reviews Count': ratings,
    'Brand': brands,
    'URL': URLs
}

df = pd.DataFrame(data)
df.to_csv("products.csv", index=False)
