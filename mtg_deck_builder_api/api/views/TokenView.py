from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import AuthToken

class TokenView(APIView):
    token_param = openapi.Parameter('token', openapi.IN_QUERY, description="Token to check", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param], operation_description="Check if token is valid",
    responses={200: "Token is valid", 400: "Bad request: missing/incorrect data", 404: "Not found: token does not exist or is not valid"})
    def get(self, request):
        token = request.query_params.get('token')
        if token is None:
            return Response({"message" : "Bad request: missing/incorrect data"},
                            status=status.HTTP_400_BAD_REQUEST)

        token_key = token[0:8]
        try:
            user = AuthToken.objects.get(token_key=token_key).user
        except AuthToken.DoesNotExist:
            return Response({"message" : "Not found: token does not exist or is not valid"},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({"user_id" : user.id})

def as_view():
    return TokenView.as_view()