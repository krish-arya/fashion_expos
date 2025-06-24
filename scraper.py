from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
                                       ElementClickInterceptedException, 
                                       TimeoutException, 
                                       StaleElementReferenceException)
import pandas as pd
import time

# Setup Chrome with options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Maximize window for better element visibility
# chrome_options.add_argument("--headless")  # Uncomment for headless mode
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.tradeindia.com/tradeshows/apparel-fashion/")

# Wait for page to load
time.sleep(3)

# Click "Accept Cookies" if present
try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
    )
    accept_button.click()
    print("✅ Accepted cookies")
except (NoSuchElementException, TimeoutException):
    print("✅ No cookie banner found")

# Click "Show More Results" until no more cards load
MAX_CLICKS = 50
clicks = 0
prev_card_count = 0

while clicks < MAX_CLICKS:
    try:
        # Get current card count
        cards = driver.find_elements(By.CLASS_NAME, "cardBox")
        current_count = len(cards)
        
        # Break if no new cards loaded
        if current_count == prev_card_count and clicks > 0:
            print("✅ No new cards loaded. Stopping.")
            break
            
        # Find and click the "Show More Results" button
        show_more_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Show More Results']]"))
        )
        
        # Scroll to button and click
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", show_more_button)
        time.sleep(0.5)
        show_more_button.click()
        
        # Wait for new cards to load
        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "cardBox")) > current_count
        )
        
        # Update card count
        prev_card_count = current_count
        clicks += 1
        print(f"✅ Clicked 'Show More Results' ({clicks} times). Cards loaded: {current_count} → {len(driver.find_elements(By.CLASS_NAME, 'cardBox'))}")
        
    except (TimeoutException, NoSuchElementException):
        print("✅ No more 'Show More Results' button found")
        break
    except (ElementClickInterceptedException, StaleElementReferenceException):
        print("🔄 Element changed, retrying...")
        time.sleep(2)
        continue

print(f"✅ Total cards loaded: {len(driver.find_elements(By.CLASS_NAME, 'cardBox'))}")

# Extract data from all cards
cards = driver.find_elements(By.CLASS_NAME, "cardBox")
events = []
print(f"⏳ Extracting data from {len(cards)} cards...")

for index, card in enumerate(cards):
    try:
        # Name
        try:
            name_elem = card.find_element(By.XPATH, ".//p[contains(@class, 'body1R')]//a")
            name = name_elem.text.strip()
        except NoSuchElementException:
            name = ""
        
        # Date
        try:
            date_elem = card.find_element(By.XPATH, ".//p[contains(@class, 'Body5R')]")
            date = date_elem.text.strip()
        except NoSuchElementException:
            date = ""
        
        # Description
        try:
            desc_elem = card.find_element(By.XPATH, ".//a[contains(@href, '/tradeshows/')]//span[contains(@class, 'Body4R')]")
            desc = desc_elem.text.strip()
            # Remove the ".....more" text if present
            if desc.endswith(".....more"):
                desc = desc[:-9].strip()
        except NoSuchElementException:
            desc = ""
        
        # Location details
        try:
            venue_elem = card.find_element(By.XPATH, ".//a[contains(@href, '/venue/')]")
            venue = venue_elem.text.strip()
        except NoSuchElementException:
            venue = ""
        
        try:
            country_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'cityCountry')]")
            country = country_elem.text.strip()
        except NoSuchElementException:
            country = ""
        
        location = f"{venue}, {country}".strip(", ")
        
        # Tags
        try:
            tag_elems = card.find_elements(By.XPATH, ".//a[contains(@class, 'btn-tag-item')] | .//span[contains(@class, 'btn-tag-item')]")
            tags = [tag.text.strip() for tag in tag_elems if tag.text.strip()]
        except NoSuchElementException:
            tags = []
        
        # Organizer website
        try:
            website_elem = card.find_element(By.XPATH, ".//a[.//p[text()='Website']]")
            website = website_elem.get_attribute("href")
        except NoSuchElementException:
            website = ""
        
        # Event URL
        try:
            event_url_elem = card.find_element(By.XPATH, ".//p[contains(@class, 'body1R')]//a")
            event_url = event_url_elem.get_attribute("href")
        except NoSuchElementException:
            event_url = ""
        
        events.append({
            "Event Name": name,
            "Date": date,
            "Description": desc,
            "Location": location,
            "Tags": ", ".join(tags),
            "Event URL": event_url,
            "Organizer Website": website
        })
        
        # Progress indicator
        if (index + 1) % 10 == 0 or (index + 1) == len(cards):
            print(f"⏳ Processed {index + 1}/{len(cards)} cards")
            
    except Exception as e:
        print(f"⚠️ Error processing card {index+1}: {str(e)}")
        continue

driver.quit()

# Save to Excel
df = pd.DataFrame(events)
df.to_excel("tradeindia_events.xlsx", index=False)
print(f"✅ Successfully scraped {len(events)} events and saved to 'tradeindia_events.xlsx'")