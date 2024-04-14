
import streamlit as st
from io import BytesIO
from email_sender import EmailSender

class EmailSenderUI:
    def __init__(self):
        self.email_sender = EmailSender()
        self.setup_ui()

    def setup_ui(self):
        st.title("FTP File Upload and Email")

        # File Path
        file_path = st.file_uploader("Pick a file")

        # Recipient Email
        recipient_email = st.text_input("Recipient Email:")

        # Subject
        subject = st.text_input("Subject:")

        # Body
        body = st.text_area("Body:", height=5)

        # Upload Button
        if st.button("Upload File and Send Email"):
            if file_path is not None:
                # Upload File
                file_content = BytesIO(file_path.read())
                file_name = file_path.name
                aux,file_url = self.email_sender.upload_file(file_content, file_name)

                if file_url:
                    # Send Email
                    email_success = self.email_sender.send_email(recipient_email, subject, body, file_url)
                    if email_success:
                        st.success("File uploaded successfully and email sent!")
                    else:
                        st.error("Email sending failed. Please check recipient email.")
                else:
                    st.error("File upload failed. Please check the file path.")
            else:
                st.warning("Please choose a file.")

        # Clear Fields Button
        if st.button("Clear Fields"):
            st.text_input("Recipient Email:").empty()
            st.text_input("Subject:").empty()
            st.text_area("Body:", height=5).empty()

if __name__ == "__main__":
    EmailSenderUI()