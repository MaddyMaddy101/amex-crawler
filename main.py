from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
import os

patterns = [
    # Standard patterns
    r'Earn\s+(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
    r'earn\s+(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
    r'(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards®?\s*Points',
    # Points back patterns
    r'up\s+to\s+(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards®?\s*points?\s+back',
    # Welcome bonus patterns
    r'welcome\s+bonus\s+of\s+(\d{2,3}(?:,\d{3})*)',
    r'Welcome\s+Offer:\s*(\d{2,3}(?:,\d{3})*)',
    # HTML specific patterns
    r'header--[^"]*">.*?(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
    r'class="[^"]*">.*?(\d{2,3}(?:,\d{3})*)\s*Membership\s+Rewards',
]

def test_patterns_on_file():
    print("\n--- Testing patterns on debug_page.html ---")
    try:
        with open('debug_page.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        
        offers = []
        for pattern in patterns:
            print(f"\nTrying pattern: {pattern}")
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    if not match:
                        continue
                    full_text = match.group(0)
                    if not full_text:
                        continue
                    value_str = match.group(1)
                    if not value_str:
                        continue
                        
                    print(f"Found text: '{full_text}'")
                    print(f"Extracted value: '{value_str}'")
                    
                    clean_value = re.sub(r'[^\d,]', '', value_str)
                    if not clean_value:
                        continue
                    value = float(clean_value.replace(',', ''))
                    
                    if value >= 10000:
                        offers.append(value)
                        print(f"Added offer: {value:,.0f} points")
                except (ValueError, AttributeError, IndexError) as e:
                    print(f"Error processing match: {e}")
                    continue
        
        if offers:
            print("\nAll found offers:", [int(x) for x in offers])
            print(f"Highest offer: {max(offers):,.0f} points")
        else:
            print("\nNo offers found in debug file!")
            # Print a sample of the content for debugging
            print("\nContent sample:")
            print(content[:500])
            
    except FileNotFoundError:
        print("debug_page.html not found!")
    except Exception as e:
        print(f"Error testing patterns: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

def play_alert():
    # Simple console bell sound
    print('\a')
    # Print visible alert
    print("\n" + "!" * 50)
    print("HIGH OFFER FOUND!")
    print("!" * 50 + "\n")

def check_for_offer():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f'--user-data-dir=/tmp/chrome-user-data-{int(time.time())}')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        while True:
            driver.get(\"https://www.americanexpress.com/us/credit-cards/business/business-credit-cards/american-express-business-gold-card-amex\")

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, \"body\")))
            time.sleep(5)

            page_content = driver.page_source

            offers = []
            for pattern in patterns:
                matches = re.finditer(pattern, page_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    value_str = match.group(1)
                    clean_value = re.sub(r'[^\\d,]', '', value_str)
                    value = float(clean_value.replace(',', ''))

                    if value >= 10000:
                        offers.append(value)
                        print(f\"Found offer: {value:,.0f} points\")

            if offers:
                max_offer = max(offers)
                print(f\"Highest offer found: {max_offer:,.0f} points\")

                if max_offer >= 200000:
                    print(\"200,000+ points offer detected! URL:\", driver.current_url)
                    break
                else:
                    print(\"Checking again in 60 seconds...\")
                    time.sleep(60)
            else:
                print(\"No valid offers found. Retrying in 60 seconds...\")
                time.sleep(60)

    except KeyboardInterrupt:
        print(\"Stopping...\")
    finally:
        driver.quit()

if __name__ == \"__main__\":
    check_for_offer()
