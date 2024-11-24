MIU Job Search Report Automation
=======================================

This repository contains a Selenium script that automates the process of logging into MIU's job search portal and submitting daily job application reports. The script runs daily using GitHub Actions and Docker.

Features
--------

*   Automates login to MIU's job search portal.
*   Handles Microsoft authentication.
*   Automatically fills and submits job application reports.
*   Uses Docker for consistent execution.
*   Runs daily using GitHub Actions.
*   Captures screenshots and logs for debugging.

Prerequisites
-------------

*   Docker (for local testing)
*   GitHub account (for automated runs)

Setup Instructions
------------------

### 1. Clone the Repository

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
    
NOTE: If you are trying to run the code on your desktop, add your credentials to your local environment, or just basically set that values as text in the code. On Powershell:
    
    setx MIU_EMAIL put_your_miu_email
    setx MIU_PASSWORD put_your_miu_password

### Step 5: Set up GitHub workflow:

Copy the workflow file from the repository to your repository.

### Step 6: Commit and Push Changes

    git add .
    git commit -m "Add Selenium script and GitHub Actions workflow"
    git push origin main
      

### Step 7: Monitor Workflow

1.  Go to the **Actions** tab of your GitHub repository.
2.  Check the status of the workflow runs.
3.  Review logs to ensure everything is working correctly.

Automated Workflow
-----------------
The script automatically runs:
* On every push to main branch
* On pull requests to main branch
* Daily at midnight (UTC)

The workflow:
1. Builds a Docker image
2. Pushes it to GitHub Container Registry
3. Runs the container with credentials
4. Captures logs and screenshots
5. Uploads artifacts for debugging

Debugging
---------
* Check the Actions tab in GitHub for workflow runs
* Download artifacts from failed runs to see screenshots
* Review logs for detailed execution information

Contributing
-----------
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Additional: Local Usage and Testing

------------
1. Pull the Docker image:
```bash
    docker pull ghcr.io/mucahitkayadan/job_search_report_automation/selenium-script:latest 
```
2. Run the Docker image:
```bash
    docker run -e MIU_EMAIL=your-miu-email-address -e MIU_PASSWORD=your-miu-stu-password -v ${PWD}/logs:/app/logs -v ${PWD}/screenshots:/app/screenshots ghcr.io/mucahitkayadan/selenium-script:latest
```
**Note:** Both Miu Microsoft and STU passwords are the same.

### TODO

- Connect to MongoDB and get the daily application number instead of randomly generated numbers.
  - Find my resume generator:
  `https://github.com/mucahitkayadan/Resume-Builder-TeX`
  
The user needs to be able to give their Resume Builder Tex (RBT) username and it should be retrieved automatically.

- Now Microsoft and STU passwords are being used same, a different secret variable may be created for the ones who does not use them with the same password.

License
-------
MIT License. See [LICENSE.md](LICENSE.md) for details.

