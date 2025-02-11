import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from typing import Dict, List

class ReminderSystem:
    def __init__(self, storage_file: str = "reminders.json"):
        self.storage_file = storage_file
        self.reminders = self.load_reminders()
        
    def load_reminders(self) -> Dict:
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"reminders": [], "email": ""}
            
    def save_reminders(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.reminders, f, indent=4)
            
    def add_reminder(self, message: str, frequency_days: int, time_str: str = None):
        # If time is not specified, use current time
        if time_str is None:
            next_reminder = datetime.datetime.now() + datetime.timedelta(days=frequency_days)
        else:
            # Parse the time string (HH:MM)
            try:
                hour, minute = map(int, time_str.split(':'))
                current_date = datetime.datetime.now()
                next_reminder = current_date.replace(hour=hour, minute=minute, second=0)
                
                # If the specified time is earlier than current time,
                # schedule it for the next occurrence
                if next_reminder <= current_date:
                    next_reminder += datetime.timedelta(days=1)
                
                # Add the frequency days
                next_reminder += datetime.timedelta(days=frequency_days - 1)
            except ValueError:
                print("Invalid time format. Using current time instead.")
                next_reminder = datetime.datetime.now() + datetime.timedelta(days=frequency_days)

        reminder = {
            "message": message,
            "frequency_days": frequency_days,
            "time_of_day": time_str if time_str else next_reminder.strftime("%H:%M"),
            "next_reminder": next_reminder.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.reminders["reminders"].append(reminder)
        self.save_reminders()
        
    def set_email(self, email: str):
        self.reminders["email"] = email
        self.save_reminders()
        
    def send_email(self, message: str):
        # Replace these with your email server details
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-email@gmail.com"  # Your Gmail address
        sender_password = "your-app-password"   # Your Gmail app password
        
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = self.reminders["email"]
        msg["Subject"] = "Reminder"
        
        msg.attach(MIMEText(message, "plain"))
        
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            print(f"Reminder sent to {self.reminders['email']}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            
    def check_reminders(self):
        current_time = datetime.datetime.now()
        updated_reminders = []
        
        print(f"\nChecking reminders at {current_time}")
        print(f"Found {len(self.reminders['reminders'])} reminders")
        
        for reminder in self.reminders["reminders"]:
            next_reminder = datetime.datetime.strptime(
                reminder["next_reminder"], 
                "%Y-%m-%d %H:%M:%S"
            )
            
            print(f"\nReminder: '{reminder['message']}'")
            print(f"Next reminder time: {next_reminder}")
            print(f"Current time: {current_time}")
            
            if current_time >= next_reminder:
                print("Reminder is due! Sending email...")
                self.send_email(reminder["message"])
                # Update next reminder time, maintaining the same time of day
                next_date = current_time + datetime.timedelta(days=reminder["frequency_days"])
                hour, minute = map(int, reminder["time_of_day"].split(':'))
                next_reminder = next_date.replace(hour=hour, minute=minute, second=0)
                
                # If the next reminder time has already passed today,
                # schedule it for tomorrow
                if next_reminder <= current_time:
                    next_reminder += datetime.timedelta(days=1)
                
                reminder["next_reminder"] = next_reminder.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Next reminder set for: {next_reminder}")
            else:
                print(f"Time until next reminder: {next_reminder - current_time}")
                
            updated_reminders.append(reminder)
            
        self.reminders["reminders"] = updated_reminders
        self.save_reminders()

def main():
    reminder_system = ReminderSystem()
    
    while True:
        print("\n1. Add reminder")
        print("2. Set email")
        print("3. Check reminders")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            message = input("Enter reminder message: ")
            frequency = int(input("Enter reminder frequency (in days): "))
            time_str = input("Enter time of day for reminder (HH:MM) or press Enter for current time: ").strip()
            if time_str:
                reminder_system.add_reminder(message, frequency, time_str)
            else:
                reminder_system.add_reminder(message, frequency)
            print("Reminder added successfully!")
            
        elif choice == "2":
            email = input("Enter your email address: ")
            reminder_system.set_email(email)
            print("Email set successfully!")
            
        elif choice == "3":
            reminder_system.check_reminders()
            
        elif choice == "4":
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 