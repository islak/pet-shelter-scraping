from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def scrape_data():
    url = "https://houstonspca.org/available-pets/"
    
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    
    html = driver.page_source
    print(html[:2000])  # first 2000 char for debugging
    
    data = []
    
    try:
        pet_cards = driver.find_elements(By.CSS_SELECTOR, '.pet-card')
        print(f"Found {len(pet_cards)} pet cards.")  # Debugging info
    
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
                print(f"Error processing a pet card: {e}")  # Debugging info
    
    except Exception as e:
        print(f"Error finding pet cards: {e}")  # Debugging info
    
    driver.quit()
    
    return pd.DataFrame(data)

def save_to_csv(df, filename):
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    df = scrape_data()
    print(df.head())  
    save_to_csv(df, 'houston_spca_data.csv')
