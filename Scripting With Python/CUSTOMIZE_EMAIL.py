import smtplib
from email.message import EmailMessage

# Read HTML content from index.html
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

email = EmailMessage()
email["From"] = "Abdul Wassay"
email["To"] = "receiver@example.com"
email["Subject"] = "🎉 You Won 1 Million Dollars!"

# Add HTML content
email.add_alternative(html_content, subtype="html")

# Send the email
with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.login("abdulwassay1005@gmail.com", "gyum ccoq mrbk ggsi")  # Use App Password
    smtp.send_message(email)
    print("HTML Email sent successfully ✅")
