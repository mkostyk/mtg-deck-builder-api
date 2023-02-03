from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

from ..models import Deck
from ..utils import *

class ChangeFormatView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)
    format_param = openapi.Parameter('format_name', openapi.IN_QUERY, description="New format", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[deck_id_param, format_param], operation_description="Change deck format",
    responses={200: "{'message': 'Deck format changed'}", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or is not yours"})
    def post(self, request):
        deck_id = request.query_params.get('deck_id')
        format_name = request.query_params.get('format_name')

        if deck_id is None or format_name is None or format_name.capitalize() not in FORMATS:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        try:
            deck = get_my_decks(request.user).filter(id=deck_id).get()
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or is not yours"},
                            status=status.HTTP_404_NOT_FOUND)

        deck.format = format_name.capitalize()
        deck.save()
        return Response({"message" : "Deck format changed"}, status=status.HTTP_200_OK)

def as_view():
    return ChangeFormatView.as_view()