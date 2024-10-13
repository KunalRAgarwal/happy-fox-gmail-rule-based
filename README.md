# Gmail Rule-Based Email Processor

## Overview
This project implements a rule-based email processor that integrates with Gmail using the Gmail API. The script fetches emails, stores them in a local database, and applies user-defined rules to automate actions such as marking emails as read or moving them to specific labels.

## Project Structure
- **`authentication.py`**: Handles Gmail API authentication.
- **`database.py`**: Contains the database setup and Email model.
- **`fetch_emails.py`**: Script to fetch emails from Gmail and save them to the database.
- **`rules_processor.py`**: Script to load rules and process emails.
- **`rules.json`**: JSON file containing user-defined rules.
- **`config.py`**: Contains global configuration settings (e.g., debug flag).

## Prerequisites
- **Python 3.8+**: Ensure Python is installed and accessible from your command line.
- **Google Cloud Project**: Create a Google Cloud project and enable the Gmail API.
- **OAuth Credentials**: Download the `credentials_oauth.json` file from the Google Developer Console.

## Setup Instructions

### Step 1: Clone the Repository
Clone this repository to your local machine:
```sh
git clone <repository-url>
cd <repository-folder>
```

### Step 2: Install Dependencies
Create a virtual environment and install the required dependencies:
```sh
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt
```

The `requirements.txt` file should contain:
```plaintext
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
sqlalchemy
```

### Step 3: Setup OAuth Credentials
1. **Download OAuth Credentials**: Download the `credentials_oauth.json` file from the Google Developer Console.
2. **Place the Credentials File**: Place the `credentials_oauth.json` file in the root directory of the project.

### Step 4: Set Up Database
The database will be automatically set up when you first run the script. SQLite is used for easy local storage:
- The database file (`emails.db`) will be created in the root folder.
- The `Email` table is defined in `database.py`.

### Step 5: Configure Global Settings
Edit the `config.py` file to configure the debug settings:
```python
# config.py
DEBUG = True  # Set to False to disable debug output
BATCH_SIZE = 10  # Set a batch size to process a limited number of emails at a time
MAX_RESULTS = 50  # Limit the number of emails fetched from Gmail in each list request
DELAY_BETWEEN_BATCHES = 2  # Delay (in seconds) between processing batches to avoid rate limiting
TOTAL_EMAILS_LIMIT = 200  # Limit total emails fetched to 200
RULES_FILE = 'rules.json'
```

### Step 6: Run the Authentication and Fetch Emails
Run the following command to authenticate with Gmail and fetch emails:
```sh
python fetch_emails.py
```
- This will start the OAuth flow. Ensure port **8080** is open to allow redirection during authentication.
- The fetched emails will be saved to the database (`emails.db`).

### Step 7: Define Rules
Define rules in the `rules.json` file. An example of a `rules.json` file is as follows:
```json
{
  "rules": [
    {
      "predicate": "all",
      "conditions": [
        {"field": "sender", "predicate": "contains", "value": "@company.com"},
        {"field": "subject", "predicate": "contains", "value": "Meeting"}
      ],
      "actions": [
        {"action": "mark_as_read"},
        {"action": "move_message", "label": "Work"}
      ]
    }
  ]
}
```

### Step 8: Run the Rule processor file for the rule
Run the following command to run the rules for the email fetched:
```sh
python rules_processor.py
```
- This will apply actions based on coditions to the rules.