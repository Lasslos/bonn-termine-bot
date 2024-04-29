import smtplib
import ssl
from email.utils import formatdate
from email.message import EmailMessage
from datetime import timezone

from appointments import *

threshold_date = datetime(2024, 6, 24, tzinfo=timezone.utc)


def notify(appointment: Appointment):
    email_data = json.load(open("email-data.json"))
    # Define user
    receiver_email = email_data["receiver_email"]
    sender_email = email_data["sender_email"]
    account = email_data["account"]
    password = email_data["password"]
    host = email_data["host"]
    port = email_data["port"]

    email = EmailMessage()
    email_content_html = f"""
<html>
<body>
<p>Dear User,</p>
<p>The service found an appointment for you:</p>
<ul>
<li>Date: {appointment.date_time}</li>
<li>Unit: {appointment.unit}</li>
<li>Duration: {appointment.duration} minutes</li>
<li>Link: <a href='{appointment.link}'>Click here to confirm the appointment</a></li>
</ul>
<p>Sincerely,<br>
Laslo Hauschild</p>
</body>
</html>
    """
    email_content_text = f"""
Dear User,

The service found an appointment for you:

Date: {appointment.date_time}
Unit: {appointment.unit}
Duration: {appointment.duration} minutes
Link: {appointment.link} (Copy and paste the link in your browser)

Sincerely,
Laslo Hauschild
    """
    email.set_content(email_content_text)
    email.add_alternative(email_content_html, subtype='html')
    # Add same content as plain text
    email["Subject"] = "Appointment found"
    email["From"] = sender_email
    email["To"] = receiver_email
    email["Date"] = formatdate(localtime=True)

    message = email.as_string()

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
