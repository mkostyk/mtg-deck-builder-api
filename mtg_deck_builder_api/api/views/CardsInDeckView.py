from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser 

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Deck, CardsInDeck, Card
from ..serializers import CardsInDeckSerializer
from ..utils import *

class CardsInDeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get cards in deck from the database",
    responses={200: CardsInDeckSerializer(many=True), 400: "Bad request: you have to specify deck id", 404: "Not found: chosen deck does not exist or is not public"})
    def get(self, request):
        queryset = CardsInDeck.objects.all()

        deck_id = request.query_params.get('deck_id')
        
        # TODO - Django shortcut, error handling
        if deck_id is not None: 
            #Checking if chosen deck is public.
            try:
                deck = get_deck_from_id(request.user, deck_id)
                    
                queryset = queryset.filter(deck = deck)
            except Deck.DoesNotExist:
                return Response({"message" : "Not found: chosen deck does not exist or is not public"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Bad request: you have to specify deck id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)
      
        serializer = CardsInDeckSerializer(queryset, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(request_body=CardsInDeckSerializer, operation_description="Add a card to a deck",
    responses={201: CardsInDeckSerializer, 400: "Bad request: missing query parameters", 404: "Not found: chosen card/deck does not exist or you are not this deck's author"})
    def post(self, request):
        card_data = JSONParser().parse(request)
        card_serializer = CardsInDeckSerializer(data=card_data)

        # Checking if we are trying to add to our own deck.
        try:
            deck = Deck.objects.get(id=card_data['deck_id'], author=request.user)
            card = Card.objects.get(id=card_data['card_id'])
        except Deck.DoesNotExist or Card.DoesNotExist:
            return Response({"message" : "Not found: chosen card/deck does not exist or you are not this deck's author"},
                            status=status.HTTP_404_NOT_FOUND)

        if card_serializer.is_valid():
            card_serializer.save(deck=deck, card=card)  # TODO - testing
            deck.last_update = datetime.now()
            deck.save()
            return Response(card_serializer.data, status=status.HTTP_201_CREATED) 

        return Response(card_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Delete cards from a deck",
    responses={200: "OK", 400: "Bad request: missing query parameters or you are not this deck's author", 404: "Not found: chosen card does not exist"})
    def delete(self, request):
        card_id = request.query_params.get('card_id')
        
        try:
            deck = CardsInDeck.objects.get(id=card_id).deck
        except CardsInDeck.DoesNotExist:
            return Response({"message" : "Bad request: chosen card does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        if deck.author == request.user:
            if card_id is None:
                # Delete all cards from a deck
                CardsInDeck.objects.filter(deck=deck).delete()
            else:
                # Delete a single card from a deck
                CardsInDeck.objects.get(id=card_id).delete()

            deck.last_update = datetime.now()
            deck.save()
        
        else:
            return Response({"message" : "Bad request: you are not this deck's author"},
                            status=status.HTTP_400_BAD_REQUEST)

        # TODO - error handling
        return Response({}, status=status.HTTP_200_OK)

def as_view():
    return CardsInDeckView.as_view()