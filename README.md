<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Selenium Automation with GitHub Actions</title>
</head>
<body>
  <h1>Selenium Automation with GitHub Actions</h1>

  <p>This repository contains a Selenium script that automates the process of logging into a website and submitting job application details. The script is scheduled to run daily using GitHub Actions.</p>

  <h2>Features</h2>
  <ul>
    <li>Automates login to the specified website.</li>
    <li>Enters job application details for the date two days ago.</li>
    <li>Uses environment variables for secure credential management.</li>
    <li>Runs daily using GitHub Actions.</li>
  </ul>

  <h2>Prerequisites</h2>
  <ul>
    <li>Python 3.x</li>
    <li>A GitHub account</li>
  </ul>

  <h2>Setup Instructions</h2>

  <h3>Step 1: Clone the Repository</h3>
  <pre><code>git clone https://github.com/your-username/your-repository.git
cd your-repository
  </code></pre>

  <h3>Step 2: Create <code>requirements.txt</code></h3>
  <p>Create a file named <code>requirements.txt</code> and add the following lines:</p>
  <pre><code>selenium~=4.21.0
webdriver-manager~=4.0.1
  </code></pre>

  <h3>Step 3: Create a Python Script</h3>
  <p>Create a file named <code>script.py</code> and add your Selenium automation script to it. This script should use environment variables for credentials and automate the necessary steps on the website.</p>

  <h3>Step 4: Set Up GitHub Secrets</h3>
  <ol>
    <li>Navigate to your GitHub repository.</li>
    <li>Go to <strong>Settings</strong> > <strong>Secrets and variables</strong> > <strong>Actions</strong>.</li>
    <li>Click <strong>New repository secret</strong> and add the following secrets:
      <ul>
        <li><code>MIU_EMAIL</code>: Your email address.</li>
        <li><code>MIU_PASSWORD</code>: Your password.</li>
      </ul>
    </li>
  </ol>

  <h3>Step 5: Create GitHub Actions Workflow</h3>
  <p>Create a directory named <code>.github/workflows</code> in the root of your repository. Inside this directory, create a YAML file named <code>main.yml</code> with the following content:</p>
  <pre><code>name: Run Selenium Script

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
  </code></pre>

  <h3>Step 6: Commit and Push Changes</h3>
  <pre><code>git add .
git commit -m "Add Selenium script and GitHub Actions workflow"
git push origin main
  </code></pre>

  <h3>Step 7: Monitor Workflow</h3>
  <ol>
    <li>Go to the <strong>Actions</strong> tab of your GitHub repository.</li>
    <li>Check the status of the workflow runs.</li>
    <li>Review logs to ensure everything is working correctly.</li>
  </ol>

  <h2>Conclusion</h2>
  <p>By following these steps, you have set up a Selenium script that runs daily using GitHub Actions. This script logs into a website, enters job application details, and submits the form. The setup ensures secure handling of credentials using GitHub Secrets.</p>

  <p>Feel free to contribute and improve the script by submitting pull requests.</p>

  <p><strong>Note:</strong> Replace <code>your-username</code> and <code>your-repository</code> with your actual GitHub username and repository name in the URLs and commands provided.</p>
</body>
</html>
