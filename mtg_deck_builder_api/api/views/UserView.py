from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import User

class UserView(APIView):
    user_id_param = openapi.Parameter('user_id', openapi.IN_QUERY, description="User id", type=openapi.TYPE_INTEGER, required=True)

    @swagger_auto_schema(operation_description="Get user from the database", manual_parameters=[user_id_param], responses=
    {200: "User found", 400: "Bad request: missing query parameters", 404: "Not found: user does not exist"})
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if user_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            return Response({"username": user.username}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message" : "Not found: user does not exist"},
                              status=status.HTTP_404_NOT_FOUND)

def as_view():
    return UserView.as_view()