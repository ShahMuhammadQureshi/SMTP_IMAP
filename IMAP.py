import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextBrowser, QMessageBox
)
import imaplib
import email
from email.header import decode_header
import smtplib

class EmailClientApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IMAP Email Client")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        self.server_label = QLabel("IMAP Server:")
        self.server_entry = QLineEdit()

        self.email_label = QLabel("Email:")
        self.email_entry = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setEnabled(False)

        self.refresh_button = QPushButton("Refresh Inbox")
        self.refresh_button.clicked.connect(self.refresh_inbox)
        self.refresh_button.setEnabled(False)

        self.email_browser = QTextBrowser()

        form_layout = QFormLayout()
        form_layout.addRow(self.server_label, self.server_entry)
        form_layout.addRow(self.email_label, self.email_entry)
        form_layout.addRow(self.password_label, self.password_entry)
        form_layout.addRow(self.login_button, self.logout_button)
        form_layout.addRow(self.refresh_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.email_browser)

        self.setLayout(main_layout)

        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px;
            }
            QTextBrowser {
                font-size: 14px;
            }
        """)

    def login(self):
        imap_server = self.server_entry.text()
        email_address = self.email_entry.text()
        password = self.password_entry.text()

        try:
            smtp_server = smtplib.SMTP_SSL(imap_server)
            smtp_server.login(email_address, password)
            smtp_server.quit()

            self.mail = imaplib.IMAP4_SSL(imap_server)
            self.mail.login(email_address, password)

            self.server_entry.setDisabled(True)
            self.email_entry.setDisabled(True)
            self.password_entry.setDisabled(True)
            self.login_button.setDisabled(True)
            self.logout_button.setEnabled(True)
            self.refresh_button.setEnabled(True)

            self.refresh_inbox()
        except Exception as e:
            self.display_message("Login Failed", f"Error: {str(e)}")
            self.login_button.setEnabled(True)

    def logout(self):
        self.mail.logout()

        self.server_entry.setDisabled(False)
        self.email_entry.setDisabled(False)
        self.password_entry.setDisabled(False)
        self.login_button.setEnabled(True)
        self.logout_button.setDisabled(True)
        self.refresh_button.setDisabled(True)

        self.email_browser.clear()

    def refresh_inbox(self):
        try:
            self.mail.select("inbox")
            status, messages = self.mail.search(None, 'ALL')

            if status == "OK":
                email_list = messages[0].split()
                latest_emails = email_list[-7:]

                self.email_browser.clear()

                for msg_num in reversed(latest_emails):
                    _, msg_data = self.mail.fetch(msg_num, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding or 'utf-8')

                            sender, encoding = decode_header(msg.get("From"))[0]
                            if isinstance(sender, bytes):
                                sender = sender.decode(encoding or 'utf-8')

                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode("utf-8")
                            else:
                                body = msg.get_payload(decode=True).decode("utf-8")

                            email_info = f"From: {sender}\nSubject: {subject}\n\n{body}\n{'=' * 50}\n"
                            self.email_browser.append(email_info)

            else:
                self.display_message("Error", "Failed to retrieve emails.")
        except Exception as e:
            self.display_message("Error", f"Error: {str(e)}")

    def display_message(self, title, message):
        QMessageBox.warning(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    email_client_app = EmailClientApp()
    email_client_app.show()

    sys.exit(app.exec_())
