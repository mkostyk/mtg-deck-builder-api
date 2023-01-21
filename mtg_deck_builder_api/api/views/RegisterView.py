from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.models import AuthToken

from ..serializers import CreateUserSerializer, UserSerializer, UserWithTokenSerializer


class RegisterView(APIView):
    @swagger_auto_schema(request_body=CreateUserSerializer, operation_description="Register a new user", 
    responses={201: UserWithTokenSerializer, 400: "Bad request: missing/incorrect data"})
    def post(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=serializer).data,
            "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_201_CREATED)


def as_view():
    return RegisterView.as_view()