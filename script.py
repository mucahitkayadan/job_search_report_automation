import os
import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load credentials from environment variables
email = os.getenv("MIU_EMAIL")
password = os.getenv("MIU_PASSWORD")
url = "https://infosys.cs.miu.edu/infosys/index.jsp"

# Calculate the date for 2 days ago
two_days_ago = datetime.now() - timedelta(days=2)
# Format the date as M/D/YYYY without leading zeros
report_date = two_days_ago.strftime("%m/%d/%Y")

# Initialize the WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open the login page
    driver.get(url)

    # Find the email input and enter the email
    email_input = driver.find_element(By.NAME, 'j_username')
    email_input.send_keys(str(email))

    # Find the password input and enter the password
    password_input = driver.find_element(By.NAME, 'j_password')
    password_input.send_keys(str(password))

    # Submit the login form
    password_input.send_keys(Keys.RETURN)

    # Wait for login to complete
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Job Search Reports')))

    # Navigate to the job application entry page
    job_search_link = driver.find_element(By.LINK_TEXT, 'Job Search Reports')
    job_search_link.click()

    # Wait for the job search report page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'resumes')))

    # Set the report date (date two days ago in M/D/YYYY format)
    driver.execute_script(f"document.getElementsByName('reportDate')[0].value = '{report_date}'")

    # Enter a random number between 10 and 15 for job applications
    job_applications = random.randint(10, 15)
    resumes_select = Select(driver.find_element(By.NAME, 'resumes'))
    resumes_select.select_by_value(str(job_applications))

    # Wait before submitting the form
    time.sleep(3)  # Wait for 3 seconds before submitting

    # Submit the form
    submit_button = driver.find_element(By.NAME, 'submitreport')
    submit_button.click()

    print(f"Entered {job_applications} job applications for {report_date}.")

finally:
    # Close the WebDriver
    time.sleep(5)  # Wait to see the result
    driver.quit()
