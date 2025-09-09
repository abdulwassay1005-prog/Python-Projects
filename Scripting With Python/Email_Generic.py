import smtplib
from email.message import EmailMessage

email = EmailMessage()
email['from'] = 'Chanayaka'
email['to'] = 'receiver@example.com'
email['subject'] = 'Test Email from Python!'

email.set_content('Hello, this is a test email from Python!')

with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.login('abdulwassay1005@gmail.com', 'gyum ccoq mrbk ggsi')  # Not your normal password
    smtp.send_message(email)
    print('Email sent successfully!')
