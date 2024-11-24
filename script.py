import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials from environment variables
email = os.getenv("MIU_EMAIL")
password = os.getenv("MIU_PASSWORD")
url = "https://infosys.cs.miu.edu/infosys/index.jsp"

def handle_login(driver: webdriver.Chrome) -> None:
    logger.info("Starting login process")
    driver.get(url)
    
    logger.info("Entering MIU credentials")
    email_input = driver.find_element(By.NAME, 'j_username')
    email_input.send_keys(str(email))
    password_input = driver.find_element(By.NAME, 'j_password')
    password_input.send_keys(str(password))
    password_input.send_keys(Keys.RETURN)

    logger.info("Waiting for Job Search Reports link")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'Job Search Reports'))
    ).click()

    logger.info("Handling Microsoft login")
    try:
        microsoft_email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0116"))
        )
        microsoft_email.clear()
        microsoft_email.send_keys(str(email))
        
        logger.info("Clicking Next")
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        next_button.click()
        
        logger.info("Entering Microsoft password")
        microsoft_pwd = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0118"))
        )
        microsoft_pwd.clear()
        microsoft_pwd.send_keys(str(password))
        
        logger.info("Clicking Sign in")
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        driver.execute_script("arguments[0].click();", sign_in_button)
        
        time.sleep(2)
        
        logger.info("Checking for Stay signed in prompt")
        try:
            stay_signed_in = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            stay_signed_in.click()
            logger.info("Clicked Stay signed in")
        except TimeoutException:
            logger.info("No Stay signed in prompt found")
            
        logger.info("Waiting for redirect to job search page")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'resumes'))
        )
        
    except TimeoutException as e:
        logger.error(f"Error during Microsoft login: {str(e)}")
        raise

def main() -> None:
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Use Google Chrome in Docker
    
    logger.info("Setting up Chrome driver")
    service = Service(ChromeDriverManager(chrome_type="google-chrome").install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    
    try:
        handle_login(driver)
        logger.info("Login successful")
        
        logger.info("Waiting for job search page")
        WebDriverWait(driver, 20).until(
            lambda driver: "apps.cs.miu.edu/jobsearch/v1/hmi/daily-job-search-report" in driver.current_url
        )
        
        fill_job_report(driver)
        logger.info("Job report submitted successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if driver:
            driver.save_screenshot('/app/screenshots/error.png')
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
