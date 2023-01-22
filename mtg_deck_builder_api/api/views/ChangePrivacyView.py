from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

from ..models import Deck
from ..utils import *

class ChangePrivacyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Change deck privacy",
    responses={200: "{'message': 'Deck privacy changed'}", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or is not yours"})
    def post(self, request):
        deck_id = request.query_params.get('deck_id')

        if deck_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        try:
            deck = get_my_decks(request.user).filter(id=deck_id).get()
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or is not yours"},
                            status=status.HTTP_404_NOT_FOUND)

        deck.private = not deck.private
        deck.save()
        return Response({"message" : "Deck privacy changed"}, status=status.HTTP_200_OK)

def as_view():
    return ChangePrivacyView.as_view()