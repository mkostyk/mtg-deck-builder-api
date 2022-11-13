from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.http import JsonResponse

from .serializers import *
from .models import *

class CardView(APIView):
    def get(self, request):
        queryset = CardsInDeck.objects.none()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')

        if id is not None:
            queryset = Card.objects.filter(id=id)
        elif name is not None:
            queryset = Card.objects.filter(card_name__icontains=name)
        elif type is not None:
            queryset = Card.objects.filter(type_line__icontains=type)

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])

        serializer = CardSerializer(queryset[:10], many=True)
        
        return JsonResponse(serializer.data) # TODO - JsonResponse

    
class DeckView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly] # TODO - tylko dany użytkownik

    def get(self, request):
        queryset = CardsInDeck.objects.none()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        user_id = request.query_params.get('user_id')

        if id is not None:
            queryset = Deck.objects.filter(id=id)
        elif name is not None:
            queryset = Deck.objects.filter(name=name)
        elif user_id is not None:
            queryset = Deck.objects.filter(user_id=user_id)          
        
        # TODO - error na /decks
        queryset = queryset.filter(private=False)
        serializer = DeckSerializer(queryset, many=True)

        return JsonResponse(serializer.data)

    def post(self, request):
        print(request)
        deck_data = JSONParser().parse(request)
        deck_serializer = DeckSerializer(data=deck_data)
        if deck_serializer.is_valid():
            deck_serializer.save()
            return JsonResponse(deck_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(deck_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CardsInDeckView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated] # TODO - tylko dany użytkownik

    def get(self, request):
        queryset = CardsInDeck.objects.none()

        deck_id = request.query_params.get('deck_id')
        
        if deck_id is not None:
            #Checking if chosen deck is public
            deck = Deck.objects.filter(id=deck_id).filter(private=False)
            if deck.exists():
                queryset = CardsInDeck.objects.filter(deck_id=deck_id)
        
        serializer = CardsInDeckSerializer(queryset, many=True)
        return JsonResponse(serializer.data)
