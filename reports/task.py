# from django_imaplib import Imap
# from django.core.mail import EmailMessage
# from .utils import process_excel_attachment

# def fetch_sales_reports():
#     imap = Imap(host='imap.example.com', username='your_email@example.com', password='your_password')
#     imap.select('INBOX')

#     # Search for emails with subject "Daily Sales Report"
#     status, messages = imap.search('SUBJECT', 'Daily Sales Report')
    
#     for msg_id in messages[0].split():
#         status, msg = imap.fetch(msg_id, '(RFC822)')
#         for response_part in msg:
#             if isinstance(response_part, tuple):
#                 email_message = EmailMessage()
#                 email_message.message().as_string(response_part[1])
                
#                 # Process attachments (assuming there is only one attachment per email)
#                 for attachment in email_message.attachments:
#                     process_excel_attachment(attachment)  # Function to process Excel file

#     imap.close()
