import datetime
import time

from database import Email, session
from authentication import authenticate_gmail
from googleapiclient.http import BatchHttpRequest
from config import DEBUG,BATCH_SIZE,MAX_RESULTS,DELAY_BETWEEN_BATCHES,TOTAL_EMAILS_LIMIT



# Callback function to handle batch response
def handle_message_details(request_id, response, exception):
    if exception is not None:
        print(f"An error occurred for request ID {request_id}: {exception}")
    else:
        headers = response['payload'].get('headers', [])
        sender = next((h['value'] for h in headers if h['name'] == 'From'), None)
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
        snippet = response.get('snippet', '')
        received_datetime = datetime.datetime.fromtimestamp(int(response['internalDate']) / 1000)
        is_read = 'UNREAD' not in response.get('labelIds', [])

        # Check if the email already exists in the database
        existing_email = session.query(Email).filter_by(message_id=request_id).first()
        if existing_email is None:
            email = Email(
                message_id=request_id,
                sender=sender,
                subject=subject,
                message_snippet=snippet,
                received_datetime=received_datetime,
                is_read=is_read,
                labels=','.join(response.get('labelIds', []))
            )
            session.add(email)
        else:
            print(f"Email ID {request_id} already exists in the database. Skipping...")

def fetch_emails(service):
    page_token = None
    total_emails_fetched = 0

    while True:
        if total_emails_fetched >= TOTAL_EMAILS_LIMIT:
            print(f"Reached the total email limit of {TOTAL_EMAILS_LIMIT}. Stopping fetch.")
            break

        print("Fetching email list...")
        results = service.users().messages().list(userId='me', maxResults=MAX_RESULTS, pageToken=page_token).execute()
        messages = results.get('messages', [])
        page_token = results.get('nextPageToken', None)

        if not messages:
            break

        # Split messages into smaller batches
        for i in range(0, len(messages), BATCH_SIZE):
            if total_emails_fetched >= TOTAL_EMAILS_LIMIT:
                print(f"Reached the total email limit of {TOTAL_EMAILS_LIMIT}. Stopping batch processing.")
                break

            batch_messages = messages[i:i + BATCH_SIZE]
            batch = BatchHttpRequest(callback=handle_message_details, batch_uri='https://gmail.googleapis.com/batch/gmail/v1')

            for msg in batch_messages:
                DEBUG and print(f"Adding message ID {msg['id']} to batch request")
                batch.add(service.users().messages().get(userId='me', id=msg['id']), request_id=msg['id'])
                total_emails_fetched += 1

                if total_emails_fetched >= TOTAL_EMAILS_LIMIT:
                    print(f"Reached the total email limit of {TOTAL_EMAILS_LIMIT}. Stopping batch processing.")
                    break

            # Execute the batch request
            batch.execute()

            # Commit the session to save all fetched emails
            session.commit()
            print("Batch emails fetched and saved to the database.")

            # Introduce a delay between batches to avoid rate limits
            time.sleep(DELAY_BETWEEN_BATCHES)

        if not page_token:
            break

if __name__ == '__main__':
    service = authenticate_gmail()
    fetch_emails(service)
