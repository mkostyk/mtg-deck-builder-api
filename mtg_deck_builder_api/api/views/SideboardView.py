from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

from ..serializers import SideboardSerializer
from ..models import Sideboard, Deck
from ..utils import *

class SideboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)
    card_id_param = openapi.Parameter('card_id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get sideboard from the database",
    responses={200: SideboardSerializer(many=True), 400: "Bad request: missing query parameters"})
    def get(self, request):
        deck_id = request.query_params.get('deck_id')

        if deck_id is not None:
            queryset = Sideboard.objects.filter(deck_id=deck_id)
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            return Response({"message" : "Not found: chosen deck does not exist or does not have sideboard"}, 
                              status=status.HTTP_404_NOT_FOUND)

        serializer = SideboardSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=SideboardSerializer(), operation_description="Add sideboard to the database",
    responses={201: SideboardSerializer, 400: "Bad request: missing query parameters"})
    def post(self, request):
        sideboard_data = JSONParser().parse(request)
        sideboard_serializer = SideboardSerializer(data=sideboard_data)

        try:
            deck = get_my_decks(request.user).get(id=sideboard_data['deck_id'])
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if sideboard_serializer.is_valid():
            sideboard_serializer.save(deck=deck)
            return Response(sideboard_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message" : "Bad request: data is not valid"}, 
                              status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(manual_parameters=[deck_id_param, card_id_param], operation_description="Delete card from sideboard",
    responses={200: "OK", 400: "Bad request: missing query parameters"})
    def delete(self, request):
        deck_id = request.query_params.get('deck_id')
        card_id = request.query_params.get('card_id')

        try:
            deck = get_my_decks(request.user).get(id=deck_id)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if card_id is not None:
            Sideboard.objects.filter(card_id=card_id, deck_id=deck_id).delete()
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)

def as_view():
    return SideboardView.as_view()