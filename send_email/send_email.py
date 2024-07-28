import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv
import os

load_dotenv()
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
sender_email = os.getenv('SENDER_EMAIL')
sender_name = os.getenv('SENDER_NAME')
receiver_email = os.getenv('RECEIVER_EMAIL')
password = os.getenv('PASSWORD')


def send(name, receiver_email, submissions_count, rank):
    # HTML template
    html_template = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Congrats - Performer of the day</title>
        <style>
            body {{
                background-color: #f2f2f2;
                padding: 16px;
                font-family: Arial, sans-serif;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background-color: #f5f5f5;
                padding: 16px 24px;
            }}
            .header img {{
                height: 32px;
            }}
            .content {{
                padding: 24px;
            }}
            .content h2 {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 16px;
            }}
            .content p {{
                color: #4a4a4a;
                margin-bottom: 16px;
            }}
            .content p.bold {{
                font-weight: bold;
            }}
            .content p.mt-4 {{
                margin-top: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-rabbit"><path d="M13 16a3 3 0 0 1 2.24 5"/><path d="M18 12h.01"/><path d="M18 21h-8a4 4 0 0 1-4-4 7 7 0 0 1 7-7h.2L9.6 6.4a1 1 0 1 1 2.8-2.8L15.8 7h.2c3.3 0 6 2.7 6 6v1a2 2 0 0 1-2 2h-1a3 3 0 0 0-3 3"/><path d="M20 8.54V4a2 2 0 1 0-4 0v3"/><path d="M7.612 12.524a3 3 0 1 0-1.6 4.3"/></svg>
            </div>
            <div class="content">
                <h2>Congrats {name},</h2>
                <p>You are among the top 10 performers of the day as you have made {submissions_count} successful submissions with rank #{rank}. Keep practicing and remain consistent. Hope to see you again with such a nice performance.</p>
                <p class="bold">Good luck!</p>
                <p class="mt-4">CLC3.tech</p>
            </div>
        </div>
    </body>
    </html>
    '''

    # Create the email content
    msg = MIMEMultipart('alternative')
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = receiver_email
    msg['Subject'] = 'Congrats - You were among the top performers of the day!'

    # Attach the HTML content to the email
    msg.attach(MIMEText(html_template, 'html'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(sender_email, password)  # Log in to the email account
        server.sendmail(sender_email, receiver_email, msg.as_string())  # Send the email
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')
    finally:
        server.quit()  # Terminate the SMTP session