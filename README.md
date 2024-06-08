MIU Job Search Report Automation
=======================================

This repository contains a Selenium script that automates the process of logging into a website and submitting job application details. The script is scheduled to run daily using GitHub Actions.

Features
--------

*   Automates login to the specified website.
*   Enters job application details for the date two days ago.
*   Uses environment variables for secure credential management.
*   Runs daily using GitHub Actions.

Prerequisites
-------------

*   Python 3.x
*   A GitHub account

Setup Instructions
------------------

### Step 1: Clone the Repository

    git clone https://github.com/mucahitkayadan/job_search_report_automation.git
    cd job_search_report_automation
      

### Step 2: Create `requirements.txt`

Create a file named `requirements.txt` and add the following lines:

    selenium~=4.21.0
    webdriver-manager~=4.0.1
      

### Step 3: Create a Python Script

Create a file named `script.py` and add your Selenium automation script to it. This script should use environment variables for credentials and automate the necessary steps on the website.

### Step 4: Set Up GitHub Secrets

1.  Navigate to your GitHub repository.
2.  Go to **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret** and add the following secrets:
    *   `MIU_EMAIL`: Your email address.
    *   `MIU_PASSWORD`: Your password.

### Step 5: Create GitHub Actions Workflow

Create a directory named `.github/workflows` in the root of your repository. Inside this directory, create a YAML file named `main.yml` with the following content:

    name: Run Selenium Script
    
    on:
      push:
        branches:
          - main
      pull_request:
        branches:
          - main
      schedule:
        - cron: '0 0 * * *'  # Runs daily at midnight
    
    jobs:
      run-selenium-script:
        runs-on: ubuntu-latest
    
        env:
          MIU_EMAIL: ${{ secrets.MIU_EMAIL }}
          MIU_PASSWORD: ${{ secrets.MIU_PASSWORD }}
    
        steps:
        - name: Checkout repository
          uses: actions/checkout@v2
    
        - name: Set up Python
          uses: actions/setup-python@v2
          with:
            python-version: '3.x'
    
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
    
        - name: Install Chrome
          run: |
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
    
        - name: Install ChromeDriver
          run: |
            sudo apt-get install -y unzip
            curl -sS -o chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip
            unzip chromedriver_linux64.zip -d /usr/local/bin/
            rm chromedriver_linux64.zip
    
        - name: Verify environment variables
          run: |
            echo "MIU_EMAIL: $MIU_EMAIL"
            echo "MIU_PASSWORD: $MIU_PASSWORD"
    
        - name: Run Selenium script
          run: |
            python script.py
      

### Step 6: Commit and Push Changes

    git add .
    git commit -m "Add Selenium script and GitHub Actions workflow"
    git push origin main
      

### Step 7: Monitor Workflow

1.  Go to the **Actions** tab of your GitHub repository.
2.  Check the status of the workflow runs.
3.  Review logs to ensure everything is working correctly.

Conclusion
----------

By following these steps, you have set up a Selenium script that runs daily using GitHub Actions. This script logs into a website, enters job application details, and submits the form. The setup ensures secure handling of credentials using GitHub Secrets.

Feel free to contribute and improve the script by submitting pull requests.

