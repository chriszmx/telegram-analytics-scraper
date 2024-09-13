from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime, timedelta

# Setup Firefox options
firefox_options = FirefoxOptions()

# Initialize the Firefox driver
driver = webdriver.Firefox(
    service=FirefoxService(GeckoDriverManager().install()),
    options=firefox_options
)

# Set window size
driver.set_window_size(1280, 1024)

# URL of the Telegram web page
url = "https://web.telegram.org/a/#-1002216788626"  # Replace with the correct URL
driver.get(url)

# Wait for manual login
print("Please log in manually and navigate to the desired chat.")
input("Press Enter when you're ready to start scraping...")

# Define chat_data list to store scraped timestamps
chat_data = []

# Function to scroll up to load more messages
def scroll_to_load_more():
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)  # Wait for the page to load more messages


# Function to parse timestamp
def parse_timestamp(timestamp):
    try:
        return datetime.strptime(timestamp, "%d %B %Y, %H:%M:%S")
    except ValueError:
        return None  # In case the format is unexpected


# Calculate the date two weeks ago
two_weeks_ago = datetime.now() - timedelta(weeks=2)

# Wait for the chat page to load and start scraping
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".message"))
    )
    print("Messages loaded successfully!")

    last_scraped_timestamp = None
    stop_scraping = False
    message_elements = []

    while not stop_scraping:
        # Find all elements that contain time attributes
        message_elements = driver.find_elements(
            By.CSS_SELECTOR, ".message .time-inner"
        )

        for time_elem in message_elements:
            try:
                full_timestamp = time_elem.get_attribute("title")
                if full_timestamp:
                    timestamp = parse_timestamp(full_timestamp)
                    if timestamp:
                        if timestamp < two_weeks_ago:
                            stop_scraping = True
                            break
                        if (last_scraped_timestamp is None or
                                timestamp != last_scraped_timestamp):
                            print(f"New timestamp found: {full_timestamp}")
                            chat_data.append({"timestamp": full_timestamp})
                            last_scraped_timestamp = timestamp
            except Exception as e:
                print(f"Error processing message: {e}")

        if not stop_scraping:
            # Scroll to load more messages
            scroll_to_load_more()

    # Save the data to a JSON file after scraping is complete
    with open("timestamps_data.json", "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=4, ensure_ascii=False)

    print(f"Scraped {len(chat_data)} timestamps and saved to timestamps_data.json")

except Exception as e:
    print(f"Error occurred: {e}")
    message_elements = driver.find_elements(By.CSS_SELECTOR, ".message .time-inner")

finally:
    # Print debugging information
    print("Scraping process completed. Preparing to close the driver.")
    print(f"Total message elements found: {len(message_elements)}")
    print("Last 5 message elements:")
    for i, elem in enumerate(message_elements[-5:], 1):
        print(f"Element {i}:")
        print(f"  Title: {elem.get_attribute('title')}")
        print(f"  HTML: {elem.get_attribute('outerHTML')[:200]}...")

    print("Closing the driver...")
    driver.quit()
    print("Driver closed successfully.")
