from ..models import User, Otp
from ..serializer.UserSerializer import UserSerializer, OtpSerializer
from .send_email_view import SendEmail
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from rest_framework.views import APIView


class PasswordResetRequestApiView(APIView):

    def post(self, request):
        email = request.data['email']
        try:
            user_object = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = UserSerializer(user_object, many=False)

        otp_object = Otp.objects.filter(user_id=user.data['id'])
        if otp_object:
            otp_object.delete()

        self.generate_otp_for_password_reset(user.data, email)

        return Response("A code has been sent to your email.Please reset your password with that code",
                        status=status.HTTP_200_OK)

    @staticmethod
    def generate_otp_for_password_reset(user, email):
        code = get_random_string(length=6, allowed_chars='1234567890')
        otp = Otp.objects.create(user_id=user['id'], code=code)
        email_body = f'Your password reset OTP : {code}'
        SendEmail.send_email('Password reset code.', email_body, 'from@poc.project', email)


class PasswordResetPostSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class PasswordResetApiView(APIView):

    @staticmethod
    def post(request):
        validation = PasswordResetPostSerializer(data=request.data)

        if not validation.is_valid():
            return Response(validation.errors, status=status.HTTP_400_BAD_REQUEST)
        data = validation.validated_data
        email = request.data['email']

        try:
            user_object = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = UserSerializer(user_object, many=False)
        user_id = user.data['id']

        requested_otp = data['code']

        otp_object = Otp.objects.get(user_id=user_id)
        otp = OtpSerializer(otp_object, many=False)
        otp = otp.data['code']

        if requested_otp == otp:
            user_object.set_password(data['password'])
            user_object.save()
            otp_object.delete()
            return Response("Password changed Successfully.", status=status.HTTP_200_OK)
        else:
            return Response("You have entered a wrong code.", status=status.HTTP_406_NOT_ACCEPTABLE)
