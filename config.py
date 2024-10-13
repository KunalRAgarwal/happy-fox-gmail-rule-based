DEBUG = False 
BATCH_SIZE = 10  # Set a batch size to process a limited number of emails at a time
MAX_RESULTS = 50  # Limit the number of emails fetched from Gmail in each list request
DELAY_BETWEEN_BATCHES = 2  # Delay (in seconds) between processing batches to avoid rate limiting
TOTAL_EMAILS_LIMIT = 500  # Limit total emails fetched to 200
RULES_FILE = 'rules.json'