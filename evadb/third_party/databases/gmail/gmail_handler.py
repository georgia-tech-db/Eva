from datetime import datetime
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from email.utils import parsedate_to_datetime
import html2text
import pandas as pd

from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)

# Define a custom class GmailHandler that inherits from DBHandler
class GmailHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        # Extract email and password from kwargs
        self.email = kwargs.get("email")  # email account
        self.password = kwargs.get("password")  # Special password
        # Set up connection details for Gmail
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.info = {}

    # Method to establish a connection to the Gmail account
    def connect(self):
        try:
            # Set up IMAP connection and login
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email, self.password)
            return DBHandlerStatus(status=True)  # Return success status
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))  # Return error status

    # Method to disconnect from the Gmail account
    def disconnect(self):
        try:
            self.mail.logout()
        except Exception as e:
            pass  # Handle logout error if needed

    # Method to check the connection status
    def check_connection(self) -> DBHandlerStatus:
        try:
            # Check if receiving a signal from the mail account
            self.mail.noop()
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))
        return DBHandlerStatus(status=True)

    # Method to get tables (folders) from the Gmail account
    def get_tables(self) -> DBHandlerResponse:
        try:
            # Define columns for the tables
            items = [["sender", str], ["receiver", str], ["day", str], ["subject", str], ["message", str]]
            # Get a list of folders in the Gmail account
            status, folder_data = self.mail.list()
            folder_list = []
            if status == "OK":
                for folder_info in folder_data:
                    # Extract folder names and create a mapping with column information
                    folder_info_str = folder_info.decode('utf-8')
                    _, folder_name = folder_info_str.split(' "/" ')
                    folder_name = folder_name.strip('"')
                    folder_name_without_prefix = folder_name.split('/')[1] if '/' in folder_name else folder_name
                    if folder_name != "[Gmail]":
                        folder_list.append(folder_name_without_prefix)
                        self.info[folder_name_without_prefix] = items

                # Create a DataFrame with table names
                tables_df = pd.DataFrame(
                    folder_list, columns=["table_name"]
                )
                return DBHandlerResponse(data=tables_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    # Method to get columns of a specific table
    def get_columns(self, table_name: str) -> DBHandlerResponse:
        # Call get_tables to populate self.info
        self.get_tables()
        try:
            # Create a DataFrame with column names and data types
            columns_df = pd.DataFrame(
                self.info[table_name], columns=["name", "dtype"])
            return DBHandlerResponse(data=columns_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    # Helper method to decode email header
    def _decode_header(self, header):
        try:
            decoded, encoding = decode_header(header)[0]
            if isinstance(decoded, bytes):
                decoded = decoded.decode(encoding or "utf-8")
            return decoded
        except Exception as e:
            return ""

    # Method to select a mailbox (folder) and retrieve emails from it
    def select(self, mailbox) -> DBHandlerResponse:
        try:
            # Select the specified mailbox
            if mailbox.lower() != "inbox":
                self.mail.select("[Gmail]/" + mailbox)
            else:
                self.mail.select(mailbox)
            # Search for all emails in the selected mailbox
            status, messages = self.mail.search(None, "ALL")
            if status == "OK":
                # Define a generator function to yield email data
                def _email_generator():
                    for num in messages[0].split():
                        _, msg_data = self.mail.fetch(num, "(RFC822)")
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        # Extract relevant email information
                        sender = self._decode_header(msg["From"])
                        receiver = self._decode_header(msg["To"])
                        subject = self._decode_header(msg["Subject"])
                        date_str = self._decode_header(msg["Date"])
                        if date_str != "":
                            date_object = parsedate_to_datetime(date_str)
                        else:
                            date_object = ""
                        body = ""
                        # Extract email body (text or HTML)
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if "attachment" not in content_disposition:
                                    payload = part.get_payload(decode=True)
                                    if payload is not None:
                                        if content_type == "text/html":
                                            body += html2text.html2text(payload.decode("utf-8", "ignore"))
                                        else:
                                            body += payload.decode("utf-8", "ignore")
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload is not None:
                                body = payload.decode("utf-8", "ignore")
                        # Yield email data as a dictionary
                        if (date_object != ""):
                            date_object = date_object.strftime("%Y-%m-%d")
                        yield {
                            "sender": str(sender),
                            "receiver": str(receiver),
                            "day": str(date_object),
                            "subject": str(subject),
                            "message": str(body)
                        }
                
                # Return a DBHandlerResponse with the data generator
                return DBHandlerResponse(
                    data=None,
                    data_generator=_email_generator(),
                )
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))