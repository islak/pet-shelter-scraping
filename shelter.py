from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def scrape_data():
    url = "https://houstonspca.org/available-pets/"
    
    options = Options()
    options.headless = False  # Set to True to run in the background
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    
    data = []
    
    while True:
        print("Scraping page:", driver.current_url)
        
        # Locate pet cards on the current page
        pet_cards = driver.find_elements(By.CSS_SELECTOR, '.pet-card')
        
        for card in pet_cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, '.pet-card__title').text.strip()
                details = card.find_elements(By.CSS_SELECTOR, '.pet-card__text-row')
                breed = details[0].find_element(By.TAG_NAME, 'span').text.strip() if len(details) > 0 else 'Unknown'
                sex = details[1].find_element(By.TAG_NAME, 'span').text.strip() if len(details) > 1 else 'Unknown'
                age = card.find_element(By.CSS_SELECTOR, 'div > span').text.strip() if card.find_element(By.CSS_SELECTOR, 'div > span') else 'Unknown'
                weight = details[2].find_element(By.TAG_NAME, 'span').text.strip() if len(details) > 2 else 'Unknown'
                
                image_url = card.find_element(By.CSS_SELECTOR, '.pet-card__image img').get_attribute('src') if card.find_element(By.CSS_SELECTOR, '.pet-card__image img') else 'Unknown'
                details_url = card.get_attribute('href') if card.get_attribute('href') else 'Unknown'
                
                animal_data = {
                    'name': name,
                    'breed': breed,
                    'sex': sex,
                    'age': age,
                    'weight': weight,
                    'image_url': image_url,
                    'details_url': details_url
                }
                data.append(animal_data)
            except Exception as e:
                print(f"Error processing a pet card: {e}")
        
        # Check for the "Next" button and navigate to the next page
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.next.page-numbers'))
            )
            next_url = next_button.get_attribute('href')
            
            if next_url:
                print("Navigating to next page:", next_url)
                driver.get(next_url)
                time.sleep(5)  # Wait for the page to load completely
            else:
                print("No more pages or 'Next' button not found.")
                break
        except Exception as e:
            print(f"Error or no more pages: {e}")
            break
    
    driver.quit()
    
    return pd.DataFrame(data)

def save_to_csv(df, filename):
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    df = scrape_data()
    print(df.head())
    save_to_csv(df, 'houston_spca_data.csv')
