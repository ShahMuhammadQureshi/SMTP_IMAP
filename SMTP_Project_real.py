import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog, QDialog
)
from PyQt5.QtGui import QFont
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import socket
import re

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 300, 150)

        self.init_ui()

    def init_ui(self):
        label_font = QFont("Arial", 12)

        self.email_label = QLabel("Your Email:")
        self.email_label.setFont(label_font)
        self.email_entry = QLineEdit()

        self.password_label = QLabel("Your Password:")
        self.password_label.setFont(label_font)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_credentials)

        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def check_credentials(self):
        email = self.email_entry.text()
        password = self.password_entry.text()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
        elif not password:
            QMessageBox.warning(self, "Invalid Password", "Please enter a password.")
        else:
            self.accept()

class EmailSenderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Email Sender")
        self.setGeometry(100, 100, 600, 400)

        self.login_dialog = LoginDialog()
        if self.login_dialog.exec_() != QDialog.Accepted:
            sys.exit()

        self.init_ui()

    def init_ui(self):
        label_font = QFont("Arial", 12)

        self.sender_email_label = QLabel("Your Email:")
        self.sender_email_label.setFont(label_font)
        self.sender_email_entry = QLineEdit()
        self.sender_email_entry.setText(self.login_dialog.email_entry.text())
        self.sender_email_entry.setReadOnly(True)

        self.sender_password_label = QLabel("Your Password:")
        self.sender_password_label.setFont(label_font)
        self.sender_password_entry = QLineEdit()
        self.sender_password_entry.setEchoMode(QLineEdit.Password)
        self.sender_password_entry.setText(self.login_dialog.password_entry.text())
        self.sender_password_entry.setReadOnly(True)

        self.to_email_label = QLabel("Recipient's Email:")
        self.to_email_label.setFont(label_font)
        self.to_email_entry = QLineEdit()

        self.smtp_server_label = QLabel("SMTP Server:")
        self.smtp_server_label.setFont(label_font)
        self.smtp_server_entry = QLineEdit()

        self.port_label = QLabel("Port:")
        self.port_label.setFont(label_font)
        self.port_entry = QLineEdit()

        self.subject_label = QLabel("Subject:")
        self.subject_label.setFont(label_font)
        self.subject_entry = QLineEdit()

        self.body_label = QLabel("Body:")
        self.body_label.setFont(label_font)
        self.body_text = QTextEdit()

        self.attach_button = QPushButton("Attach File")
        self.attach_button.clicked.connect(self.attach_file)

        self.send_button = QPushButton("Send Email")
        self.send_button.clicked.connect(self.send_email)

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.log_out)
        self.logout_button.setStyleSheet("background-color: red;")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.attach_button)
        button_layout.addWidget(self.logout_button)
        button_layout.addWidget(self.send_button)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.sender_email_label)
        input_layout.addWidget(self.sender_email_entry)
        input_layout.addWidget(self.sender_password_label)
        input_layout.addWidget(self.sender_password_entry)
        input_layout.addWidget(self.to_email_label)
        input_layout.addWidget(self.to_email_entry)
        input_layout.addWidget(self.smtp_server_label)
        input_layout.addWidget(self.smtp_server_entry)
        input_layout.addWidget(self.port_label)
        input_layout.addWidget(self.port_entry)
        input_layout.addWidget(self.subject_label)
        input_layout.addWidget(self.subject_entry)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.body_label)
        main_layout.addWidget(self.body_text)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.attachment_path = None

    def attach_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path:
            self.attachment_path = file_path
            QMessageBox.information(self, "Attachment", f"File attached: {os.path.basename(file_path)}")

    def send_email(self):
        sender_email = self.sender_email_entry.text()
        sender_password = self.sender_password_entry.text()
        to_email = self.to_email_entry.text()
        subject = self.subject_entry.text()
        body = self.body_text.toPlainText()
        smtp_server = self.smtp_server_entry.text()
        port = self.port_entry.text()

        try:
            # Check if the SMTP server is reachable
            socket.create_connection((smtp_server, int(port)), timeout=5)

            with smtplib.SMTP(smtp_server, int(port)) as server:
                server.starttls()
                server.login(sender_email, sender_password)

                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = to_email
                message['Subject'] = subject

                message.attach(MIMEText(body, 'plain'))

                if self.attachment_path:
                    self.attach_file_to_message(message, self.attachment_path)

                server.sendmail(sender_email, to_email, message.as_string())

            QMessageBox.information(self, "Success", "Email sent successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error sending email: {str(e
            )}")

    def attach_file_to_message(self, message, file_path):
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            message.attach(part)

    def log_out(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Adding some style to make the GUI colorful
    app.setStyleSheet("""
        QWidget {
            background-color: #808080; /* Set background color to gray */
        }
        QLabel {
            color: #ffffff; /* Set text color to white */
        }
        QLineEdit, QTextEdit {
            background-color: #fff;
            color: #333;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 4px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 12px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton#logout_button {
            background-color: red;
        }
    """)
    
    email_app = EmailSenderApp()
    email_app.show()
    sys.exit(app.exec_())
