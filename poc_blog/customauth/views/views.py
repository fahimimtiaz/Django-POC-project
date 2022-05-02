from rest_framework.viewsets import ModelViewSet
from ..models import Otp
from .send_email_view import SendEmail
from django.contrib.auth import get_user_model
from ..serializer.UserSerializer import UserSerializer, OtpSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from rest_framework.views import APIView

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request):
        is_super_user = request.user.is_superuser
        if is_super_user:
            try:
                users = User.objects.all()
                serializer = UserSerializer(users, many=True)
                return Response(serializer.data)
            except Exception as ex:
                raise NotFound(ex)
        else:
            return Response("You haven't access to show all users", status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        is_super_user = request.user.is_superuser
        user_id = request.user.id
        user = self.get_object()
        if is_super_user or user.id == user_id:
            serialized_data = UserSerializer(user, many=False)
            return Response(serialized_data.data)
        else:
            return Response("You haven't access to show this user.", status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        request.data['is_active'] = False
        serialized_data = UserSerializer(data=request.data.copy())
        if serialized_data.is_valid():
            serialized_data.save()
            self.generate_otp_for_account_activation(serialized_data.data)
            return Response(("A code has been sent to your email.Please active your account with that code",
                         serialized_data.data), status=status.HTTP_201_CREATED)

        return Response("a problem has occurred.", status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

    def destroy(self, request, pk, *args, **kwargs):
        is_super_user = request.user.is_superuser
        if is_super_user:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("You haven't access to delete an user", status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, pk, *args, **kwargs):
        user_id = request.user.id
        instance = self.get_object()

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if instance.id == user_id:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response("Invalid Serialization")
        else:
            return Response("UnAuthorized")

    @staticmethod
    def generate_otp_for_account_activation(user):
        code = get_random_string(length=6, allowed_chars='1234567890')
        otp = Otp.objects.create(user_id=user['id'], code=code)
        email = user['email']
        email_body = f'Your account activation code : {code}'
        SendEmail.send_email('Account activation code.', email_body, 'from@poc.project', email)


class ActiveAccount(APIView):

    def post(self, request, pk):

        try:
            user_object = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            otp_object = Otp.objects.get(user_id=pk)
        except Otp.DoesNotExist:
            return Response("User is already an active user.", status=status.HTTP_400_BAD_REQUEST)

        otp = OtpSerializer(otp_object, many=False)

        if request.data['code'] == otp.data['code']:
            active_status = {"is_active": True}
            serializer = UserSerializer(user_object, data=active_status, partial=True)
            if serializer.is_valid():
                serializer.save()
                otp_object.delete()
            return Response("Account Activated Successfully.", status=status.HTTP_200_OK)
        else:
            return Response("You have entered a wrong code.", status=status.HTTP_406_NOT_ACCEPTABLE)


