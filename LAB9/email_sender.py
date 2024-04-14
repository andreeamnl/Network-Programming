import ftplib
import smtplib
from email.mime.text import MIMEText
from io import BytesIO

class EmailSender:
    def __init__(self):
        self.ftp = ftplib.FTP('138.68.98.108')
        self.ftp.login(user='yourusername', passwd='yourusername')

    def upload_file(self, file_content, file_name):
        try:
            self.ftp.cwd('faf-212')

            dirs = ['Andreea']
            for directory in dirs:
                try:
                    self.ftp.cwd(directory)
                except ftplib.error_perm:
                    self.ftp.mkd(directory)
                    self.ftp.cwd(directory)

            file_content.seek(0)
            self.ftp.storbinary(f'STOR {file_name}', file_content)

            file_url = f"ftp://yourusername:yourusername@138.68.98.108/faf-212/Andreea/{file_name}"
            return True, file_url
        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return False, None

    def send_email(self, recipient_email, subject, body, file_url):
        try:
            sender = 'andreeaprtest@gmail.com' 
            password = 'vdjz hfhv ypyb asfp'
            msg = MIMEText(f"{body}\n\nFile URL: {file_url}")
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient_email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipient_email, msg.as_string())

            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
