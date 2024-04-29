from datetime import timezone
from appointments import *
import smtplib, ssl

threshold_date = datetime(2024, 6, 24, tzinfo=timezone.utc)


def notify(appointment: Appointment):
    email_data = json.load(open("email-data.json"))
    # Define user
    receiver_email = email_data["receiver_email"]
    message = f"""\
    Subject: Appointment reminder
    
    The service found an appointment for you:
    Date: {appointment.date_time}
    Unit: {appointment.unit}
    Duration: {appointment.duration} minutes
    Link: {appointment.link}
    
    Please visit the link to confirm the appointment.
    
    Sincerely,
    Laslo Hauschild
    """
    sender_email = email_data["sender_email"]
    account = email_data["account"]
    password = email_data["password"]
    host = email_data["host"]
    port = email_data["port"]

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(account, password)
        server.sendmail(sender_email, receiver_email, message)


def main():
    appointments = get_appointments()
    for appointment in appointments:
        if (threshold_date - appointment.date_time).days >= 0:
            notify(appointment)


if __name__ == "__main__":
    main()
