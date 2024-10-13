import json
import time
from database import Email, session
from config import DEBUG, RULES_FILE
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
from authentication import authenticate_gmail

def load_rules():
    try:
        print("Loading rules from rules.json...")
        with open(RULES_FILE, 'r') as f:
            rules = json.load(f)['rules']
            print("Rules loaded successfully.")
            return rules
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Error loading rules: {e}')
        return []

def match_condition(email, condition):
    field = condition['field']
    predicate = condition['predicate']
    value = condition['value']

    # Get the value of the field from the email object
    email_value = getattr(email, field, None)
    if email_value is None:
        return False

    # Convert is_read field from string to boolean
    if field == 'is_read':
        email_value = bool(email_value)
        value = value.lower() == 'true'

    # Convert value to the correct type for comparison
    if field == 'received_datetime':
        value = int(value)  # Assuming value represents days

    DEBUG and print(f"Checking condition: Field={field}, Predicate={predicate}, Value={value}")

    # Matching based on the predicate
    if predicate == 'contains':
        return value in email_value
    elif predicate == 'does_not_contain':
        return value not in email_value
    elif predicate == 'equals':
        return email_value == value
    elif predicate == 'does_not_equal':
        return email_value != value
    elif predicate == 'less_than' and isinstance(email_value, datetime):
        return email_value < datetime.now() - timedelta(days=value)
    elif predicate == 'greater_than' and isinstance(email_value, datetime):
        return email_value > datetime.now() - timedelta(days=value)
    return False

def apply_rules(service, rules):
    emails = session.query(Email).all()
    print(f"Applying rules to {len(emails)} emails...")
    for email in emails:
        for rule in rules:
            conditions = rule['conditions']
            predicate = rule['predicate']

            if predicate == 'all':
                match = all(match_condition(email, cond) for cond in conditions)
            elif predicate == 'any':
                match = any(match_condition(email, cond) for cond in conditions)
            else:
                match = False

            if match:
                print(f"Email ID {email.message_id} matches rule, applying actions...")
                apply_actions(service, email, rule['actions'])

def apply_actions(service, email, actions):
    for action in actions:
        if action['action'] == 'mark_as_read':
            print(f"Marking email ID {email.message_id} as read...")
            modify_message(service, email.message_id, {'removeLabelIds': ['UNREAD']})
            # Update the database
            email.is_read = True
        elif action['action'] == 'mark_as_unread':
            print(f"Marking email ID {email.message_id} as unread...")
            modify_message(service, email.message_id, {'addLabelIds': ['UNREAD']})
            # Update the database
            email.is_read = False
        elif action['action'] == 'move_message':
            label = action['label']
            print(f"Moving email ID {email.message_id} to label {label}...")
            # Check if label exists or create it
            try:
                existing_labels = service.users().labels().list(userId='me').execute().get('labels', [])
                label_ids = [lbl['id'] for lbl in existing_labels if lbl['name'].lower() == label.lower()]

                if not label_ids:
                    # Label does not exist, create it
                    new_label = create_label(service, label)
                    if new_label:
                        label_ids.append(new_label['id'])

                if label_ids:
                    modify_message(service, email.message_id, {'addLabelIds': label_ids})
                else:
                    if DEBUG:
                        print(f"Failed to create or find the label '{label}'.")

            except HttpError as error:
                if DEBUG:
                    print(f'An error occurred: {error}')

    # Commit the changes to the database after applying actions
    try:
        session.commit()
    except Exception as e:
        if DEBUG:
            print(f"An error occurred while updating the database: {e}")
        session.rollback()

def modify_message(service, message_id, modifications, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Modifying message ID: {message_id} with modifications: {modifications}")
            service.users().messages().modify(userId='me', id=message_id, body=modifications).execute()
            print(f"Modification successful for message ID: {message_id}")
            break
        except HttpError as error:
            if error.resp.status in [429, 500, 503]:
                # These are retryable errors, so we add a delay and retry
                wait_time = (2 ** attempt)
                print(f"Retrying due to error: {error}. Waiting {wait_time} seconds.")
                time.sleep(wait_time)
            else:
                print(f'An error occurred: {error}')
                break

def create_label(service, label_name):
    label_body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }
    try:
        label = service.users().labels().create(userId='me', body=label_body).execute()
        if DEBUG:
            print(f"Label '{label_name}' created successfully.")
        return label
    except HttpError as error:
        if DEBUG:
            print(f"An error occurred while creating the label '{label_name}': {error}")
        return None

if __name__ == '__main__':
    service = authenticate_gmail()
    rules = load_rules()
    apply_rules(service, rules)
