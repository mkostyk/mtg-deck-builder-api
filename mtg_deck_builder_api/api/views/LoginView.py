from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer

from drf_yasg.utils import swagger_auto_schema

from knox.views import LoginView as KnoxLoginView

from ..serializers import ResponseTokenSerializer

class LoginView(KnoxLoginView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=AuthTokenSerializer, operation_description="Login a user",
    responses={200: ResponseTokenSerializer, 400: "Bad request: missing/incorrect data"})

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']  # type: ignore # Nie wiem czemu to krzyczy bo działa
        login(request, user)
        return super(LoginView, self).post(request, format=None)

def as_view():
    return LoginView.as_view()