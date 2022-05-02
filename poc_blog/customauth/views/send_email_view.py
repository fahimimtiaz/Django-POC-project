from rest_framework.views import APIView
from django.core import mail
connection = mail.get_connection()


class SendEmail(APIView):

    @staticmethod
    def send_email(subject, otp, email_from, email_to):
        connection.open()

        email1 = mail.EmailMessage(
            subject,
            otp,
            email_from,
            [email_to],
            connection=connection,
        )
        email1.send()
        connection.close()