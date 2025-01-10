import os
import time
import random
from datetime import datetime, timedelta
import logging
import platform

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials from environment variables
email = os.getenv("MIU_EMAIL")
password = os.getenv("MIU_PASSWORD")
url = "https://apps.cs.miu.edu/jobsearch/v1/hmi/daily-job-search-report?continue"

def login(driver):
    logger.info("Starting login process")
    
    # Verify environment variables
    logger.info(f"Email value: {email}")
    if not email or not password:
        raise ValueError("Email or password environment variables are not set")
    
    try:
        # Navigate to URL
        driver.get(url)
        logger.info("Navigated to login page")
        
        # Wait for page to stabilize
        time.sleep(2)
        
        # Log current URL
        logger.info(f"Current URL: {driver.current_url}")
        
        # Wait for email field using JavaScript
        logger.info("Attempting to interact with email field using JavaScript...")
        try:
            # Wait for email field to be present
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.getElementById('i0116') !== null")
            )
            
            # Verify email value before injection
            logger.info(f"About to enter email: {email[:3]}...") # Only log first 3 chars
            
            # Enter email using JavaScript with escaped quotes
            js_script = f"""
                var emailInput = document.getElementById('i0116');
                emailInput.value = "{email}";
                emailInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            """
            driver.execute_script(js_script)
            
            # Verify the value was set
            entered_value = driver.execute_script("return document.getElementById('i0116').value")
            logger.info(f"Verified entered value: {entered_value[:3]}...") # Only log first 3 chars
            
            logger.info("Email entered using JavaScript")
            
            # Small delay
            time.sleep(1)
            
            # Click Next button using JavaScript
            driver.execute_script("""
                var nextButton = document.getElementById('idSIButton9');
                if(nextButton) nextButton.click();
            """)
            logger.info("Clicked Next button")
            
            # Wait for password field
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.querySelector('input[name=\"passwd\"]') !== null")
            )
            
            # Enter password using JavaScript
            js_script = f"""
                var passwordInput = document.querySelector('input[name="passwd"]');
                passwordInput.value = '{password}';
                passwordInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            """
            driver.execute_script(js_script)
            logger.info("Password entered using JavaScript")
            
            # Small delay
            time.sleep(1)
            
            # Click Sign in button using JavaScript
            driver.execute_script("""
                var signInButton = document.getElementById('idSIButton9');
                if(signInButton) signInButton.click();
            """)
            logger.info("Clicked Sign in button")
            
            # Handle "Stay signed in?" prompt more explicitly
            logger.info("Waiting for 'Stay signed in?' prompt...")
            try:
                # Wait specifically for the prompt text
                WebDriverWait(driver, 10).until(
                    lambda d: "Stay signed in?" in d.page_source
                )
                
                # Click "Yes" using JavaScript
                yes_script = """
                    var buttons = document.querySelectorAll('input[type="submit"]');
                    for(var button of buttons) {
                        if(button.value === 'Yes') {
                            button.click();
                            break;
                        }
                    }
                """
                driver.execute_script(yes_script)
                logger.info("Clicked 'Yes' on 'Stay signed in?' prompt")
                
                # Wait for the prompt to disappear
                time.sleep(3)
                
            except TimeoutException:
                logger.info("No 'Stay signed in?' prompt found")
            
            # Wait for redirect to complete
            time.sleep(5)
            logger.info("Login sequence completed")
            
        except Exception as e:
            logger.error(f"JavaScript interaction failed: {str(e)}")
            driver.save_screenshot("js_error.png")
            raise
            
    except Exception as e:
        logger.error(f"Login failed with error: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fill_job_report(driver):
    logger.info("Starting to fill job report")
    try:
        # Wait for redirect to the job search page with correct URL
        logger.info("Waiting for job search page to load...")
        WebDriverWait(driver, 20).until(
            lambda driver: "apps.cs.miu.edu/jobsearch/v1/hmi/daily-job-search-report" in driver.current_url
        )
        logger.info(f"Current URL: {driver.current_url}")
        
        # Wait for form to be fully loaded
        logger.info("Waiting for form elements...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "toDate"))
        )
        
        # Calculate the date (2 days ago)
        two_days_ago = datetime.now() - timedelta(days=2)
        report_date = two_days_ago.strftime("%Y-%m-%d")  # Using YYYY-MM-DD format for HTML5 date input
        logger.info(f"Setting report date to: {report_date}")

        # Set the date using JavaScript
        date_script = f"""
            let dateInput = document.getElementById('toDate');
            dateInput.value = '{report_date}';
            dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """
        driver.execute_script(date_script)
        logger.info("Date set successfully")

        # Verify date was set
        current_date = driver.execute_script("return document.getElementById('toDate').value")
        logger.info(f"Verified date value: {current_date}")

        # Small delay after setting date
        time.sleep(2)

        # Generate random number of applications
        job_applications = random.randint(10, 15)
        logger.info(f"Setting number of applications to: {job_applications}")

        # Set the number of applications
        applications_script = f"""
            let select = document.getElementById('resumes');
            select.value = '{job_applications}';
            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """
        driver.execute_script(applications_script)
        logger.info(f"Set {job_applications} job applications")

        # Small delay before submitting
        time.sleep(2)

        # Click the submit button
        submit_script = """
            document.getElementById('submitButton').click();
        """
        driver.execute_script(submit_script)
        logger.info("Clicked submit button")

        # Wait for submission confirmation
        time.sleep(3)
        logger.info("Report submission completed")

    except Exception as e:
        logger.error(f"Error filling form: {str(e)}")
        driver.save_screenshot("form_error.png")
        # Log the page source for debugging
        with open("form_error.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    
    # Add common options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Configure based on platform
    if platform.system() == "Windows":
        chrome_options.add_argument("--remote-debugging-port=9222")
        # Add this to prevent detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
    else:
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = "/usr/bin/google-chrome"
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.205 Safari/537.36"
    })
    
    # Remove navigator.webdriver flag
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def main():
    start_time = datetime.now()
    driver = None
    try:
        logger.info(f"Starting job report automation at {start_time}")
        driver = setup_driver()
        
        login(driver)
        logger.info("Login successful")
        
        fill_job_report(driver)
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Job report automation completed successfully in {duration}")
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        if driver:
            try:
                driver.save_screenshot(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                with open(f"error_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
            except:
                logger.error("Failed to save error evidence")
        raise
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
