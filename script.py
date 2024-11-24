import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional
import logging
import pytz

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

load_dotenv()
# Load credentials from environment variables
email = os.getenv("MIU_EMAIL_")
password = os.getenv("MIU_PASSWORD_")
url = "https://infosys.cs.miu.edu/infosys/index.jsp"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def handle_login(driver: webdriver.Chrome) -> None:
    """
    Handle the login process including MIU login and Microsoft authentication.
    
    Args:
        driver: Chrome WebDriver instance
        
    Raises:
        TimeoutException: If login elements are not found within timeout period
    """
    try:
        logger.info("Starting login process")
        driver.get(url)
        
        logger.info("Entering credentials")
        email_input = driver.find_element(By.NAME, 'j_username')
        email_input.send_keys(str(email))
        password_input = driver.find_element(By.NAME, 'j_password')
        password_input.send_keys(str(password))
        password_input.send_keys(Keys.RETURN)
        
        logger.info("Handling Microsoft login redirect")
        # Click on Job Search Reports and wait for Microsoft redirect
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Job Search Reports'))
        ).click()
        
        # Handle Microsoft login after redirect
        try:
            # Wait for Microsoft login email field
            microsoft_email = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "i0116"))
            )
            microsoft_email.clear()
            microsoft_email.send_keys(str(email))
            
            # Click Next
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            next_button.click()
            
            # Wait for password field and enter password
            microsoft_pwd = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "i0118"))
            )
            microsoft_pwd.clear()
            microsoft_pwd.send_keys(str(password))
            
            # Try multiple methods to click the sign in button
            try:
                # Method 1: Wait and click
                sign_in_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Sign in']"))
                )
                sign_in_button.click()
            except:
                try:
                    # Method 2: JavaScript click
                    sign_in_button = driver.find_element(By.ID, "idSIButton9")
                    driver.execute_script("arguments[0].click();", sign_in_button)
                except:
                    # Method 3: Submit form
                    sign_in_button = driver.find_element(By.ID, "idSIButton9")
                    sign_in_button.submit()
            
            # Add a small delay after clicking
            time.sleep(2)
            
            # Handle "Stay signed in?" prompt if it appears
            try:
                stay_signed_in = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Yes']"))
                )
                stay_signed_in.click()
            except TimeoutException:
                pass
            
            # Wait for redirect back to the job search page
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'resumes'))
            )
            
        except TimeoutException as e:
            print(f"Error during Microsoft login: {str(e)}")
            raise
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise

def fill_job_report(driver: webdriver.Chrome) -> None:
    """
    Fill out the job search report form with random number of applications.
    
    Args:
        driver: Chrome WebDriver instance
        
    Raises:
        Exception: If there are any errors during form filling
    """
    try:
        logger.info("Starting to fill job report")
        
        # Wait for the form to be fully loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'toDate'))
        )
        
        # Calculate and log the date being used
        two_days_ago = datetime.now(pytz.timezone('US/Central')) - timedelta(days=2)
        report_date = two_days_ago.strftime("%Y-%m-%d")
        logger.info(f"Using report date: {report_date}")
        
        # Set the date using JavaScript
        date_script = f"""
            let dateInput = document.getElementById('toDate');
            dateInput.value = '{report_date}';
            dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """
        driver.execute_script(date_script)
        
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
        
        # Wait a moment for the selection to register
        time.sleep(2)
        
        # Click the submit button
        submit_script = """
            document.getElementById('submitButton').click();
        """
        driver.execute_script(submit_script)
        
        logger.info(f"Reporting {job_applications} job applications")
        
        # Verify submission
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )
            logger.info("Form submitted successfully")
        except TimeoutException:
            logger.error("Could not verify form submission")
            raise
        
        # Wait for submission to complete
        time.sleep(3)
        
    except Exception as e:
        logger.error(f"Error filling form: {str(e)}")
        # Get the current value of the date field for debugging
        current_date = driver.execute_script("return document.getElementById('toDate').value")
        print(f"Current date value: {current_date}")
        raise

def capture_screenshot(driver, name):
    try:
        # Ensure screenshots directory exists
        os.makedirs('/app/screenshots', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"/app/screenshots/{name}_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {str(e)}")

def main() -> None:
    """
    Main function to run the job search report automation.
    Sets up the Chrome WebDriver and executes the login and form filling process.
    """
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Updated binary location
    
    # Setup Chrome driver with version detection
    service = Service(ChromeDriverManager(chrome_type="google-chrome").install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    
    try:
        handle_login(driver)
        
        # Wait for redirect to complete and URL to change
        WebDriverWait(driver, 20).until(
            lambda driver: "apps.cs.miu.edu/jobsearch/v1/hmi/daily-job-search-report" in driver.current_url
        )
        
        fill_job_report(driver)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        capture_screenshot(driver, "error")
        raise
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()
