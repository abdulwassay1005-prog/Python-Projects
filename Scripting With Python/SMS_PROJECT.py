# sms_project.py
# A simple Python SMS simulation without external services

def send_sms(phone_number, message):
    # This is just a simulation
    print("===================================")
    print(f"Sending SMS to {phone_number}...")
    print(f"Message: {message}")
    print("✅ SMS sent successfully (simulation).")
    print("===================================")

def main():
    print("=== Simple SMS App ===")
    to_number = input("Enter phone number (e.g., +923001234567): ")
    text = input("Enter your message: ")
    send_sms(to_number, text)

if __name__ == "__main__":
    main()
