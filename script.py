import os
import time
import random
from datetime import datetime, timedelta
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

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
        # Wait for and enter email
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0116"))
        ).send_keys(str(email))
        
        logger.info("Clicking Next")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        ).click()
        
        # Wait for page transition
        time.sleep(2)
        
        logger.info("Entering Microsoft password")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0118"))
        ).send_keys(str(password))
        
        logger.info("Clicking Sign in")
        # Find the button again to avoid stale element
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        ).click()
        
        # Wait for page transition
        time.sleep(2)
        
        logger.info("Checking for Stay signed in prompt")
        try:
            # Find the button again for "Stay signed in"
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            ).click()
            logger.info("Clicked Stay signed in")
        except TimeoutException:
            logger.info("No Stay signed in prompt found")
            
        logger.info("Waiting for redirect to job search page")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'resumes'))
        )
        
    except TimeoutException as e:
        logger.error(f"Error during Microsoft login: {str(e)}")
        driver.save_screenshot('/app/screenshots/login_error.png')
        raise

def fill_job_report(driver: webdriver.Chrome) -> None:
    logger.info("Starting to fill job report")
    try:
        # Wait for the form to be fully loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'toDate'))
        )
        logger.info("Form loaded successfully")

        # Calculate the date
        two_days_ago = datetime.now() - timedelta(days=2)
        report_date = two_days_ago.strftime("%Y-%m-%d")
        logger.info(f"Setting report date to: {report_date}")

        # Set the date using JavaScript
        date_script = f"""
            let dateInput = document.getElementById('toDate');
            dateInput.value = '{report_date}';
            dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """
        driver.execute_script(date_script)
        logger.info("Date set successfully")

        # Wait a moment for the date to register
        time.sleep(2)

        # Select random number of applications
        job_applications = random.randint(10, 15)
        select_script = f"""
            let select = document.getElementById('resumes');
            select.value = '{job_applications}';
            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """
        driver.execute_script(select_script)
        logger.info(f"Selected {job_applications} job applications")

        # Wait a moment for the selection to register
        time.sleep(2)

        # Click the submit button
        submit_script = """
            document.getElementById('submitButton').click();
        """
        driver.execute_script(submit_script)
        logger.info("Clicked submit button")

        # Wait for submission to complete
        time.sleep(3)
        logger.info(f"Successfully submitted report: {job_applications} applications for {report_date}")

    except Exception as e:
        logger.error(f"Error filling form: {str(e)}")
        # Get the current value of the date field for debugging
        try:
            current_date = driver.execute_script("return document.getElementById('toDate').value")
            logger.error(f"Current date value when error occurred: {current_date}")
        except:
            pass
        driver.save_screenshot('/app/screenshots/form_error.png')
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
