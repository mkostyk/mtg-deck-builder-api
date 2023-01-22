from django.db.models import Q
from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

from ..serializers import DeckSerializer, DeckPostRequestSerializer
from ..models import Deck, CardsInDeck
from ..utils import *

class DeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)
    name_param = openapi.Parameter('name', openapi.IN_QUERY, description="Deck name", type=openapi.TYPE_STRING)
    user_id_param = openapi.Parameter('user_id', openapi.IN_QUERY, description="User id", type=openapi.TYPE_INTEGER)
    page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1)

    @swagger_auto_schema(manual_parameters=[id_param, name_param, user_id_param, page_param], operation_description="Get decks from the database",
    responses={200: DeckSerializer(many=True), 400: "Bad request: missing query parameters", 404: "Not found: user/deck does not exist or is private"})
    def get(self, request):
        queryset = Deck.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        user_id = request.query_params.get('user_id')
        page = get_page(request.query_params.get('page'))

        if id is None and name is None and user_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        # Filtering by query parameters
        if id is not None:
            queryset = queryset.filter(id=id)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if user_id is not None:
            try:
                if user_id == "-1" and not request.user.is_anonymous: # why string?
                    user = request.user
                else:
                    user = User.objects.get(id=user_id)
                    
                queryset = queryset.filter(author=user)
            except User.DoesNotExist:
                return Response({"message" : "Not found: user does not exist"},
                                  status=status.HTTP_404_NOT_FOUND)

        # Filtering private decks
        if not request.user.is_anonymous:
            queryset = queryset.filter(Q(private=False) | Q(author=request.user))
        else:
            queryset = queryset.filter(private=False)

        if not queryset.exists():
            return Response({"message" : "Not found: deck does not exist or is private."},
                            status=status.HTTP_404_NOT_FOUND)

        start = (page - 1) * PAGE_SIZE
        end = page * PAGE_SIZE
        
        serializer = DeckSerializer(queryset[start:end], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    copy_id = openapi.Parameter('copy_id', openapi.IN_QUERY, description="Deck id to copy", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(request_body=DeckPostRequestSerializer(), manual_parameters=[copy_id], 
    operation_description="Create a new deck", responses={201: DeckSerializer,
    400: "Bad request: missing query parameters", 404: "Not found: deck to copy does not exist"})
    def post(self, request):
        deck_data = JSONParser().parse(request)
        deck_data['author'] = request.user.id
        deck_data['votes'] = 0

        if deck_data['format'] not in FORMATS:
            return Response({"message" : "Bad request: invalid deck format"},
                            status=status.HTTP_400_BAD_REQUEST)

        deck_serializer = DeckSerializer(data=deck_data)

        copying_id = request.query_params.get('copy_id')

        if deck_serializer.is_valid():
            deck_serializer.save()
            if copying_id is not None:
                try:
                    deck = get_deck_from_id(request.user, copying_id)
                    cards = CardsInDeck.objects.filter(deck=deck)
                    for card in cards:
                        CardsInDeck.objects.create(deck=deck_serializer.instance, card=card.card)
                except Deck.DoesNotExist:
                    return Response({"message" : "Not found: deck to copy does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)

            return Response(deck_serializer.data, status=status.HTTP_201_CREATED) 

        return Response(deck_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(manual_parameters=[id_param], operation_description="Delete a deck",
    responses={200: "OK", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or you are not its author"})
    def delete(self, request):
        deck_id = request.query_params.get('id') # TODO - (name, user_id) jako unique key

        if deck_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        # Checking if we are deck's author
        try:
            deck = Deck.objects.get(id=deck_id, author=request.user)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or you are not its author"},
                            status=status.HTTP_404_NOT_FOUND)

        deck.delete()

        # TODO - error handling
        return Response({}, status=status.HTTP_200_OK)

def as_view():
    return DeckView.as_view()