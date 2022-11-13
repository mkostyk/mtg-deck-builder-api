from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import get_list_or_404 # TODO - use this

from .serializers import *
from .models import *

# TODO - error codes
# TODO - JsonResponse

# TODO - error handling
class CardView(APIView):
    def get(self, request):
        queryset = CardsInDeck.objects.none()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')

        if id is not None:
            queryset = Card.objects.filter(id=id)
        if name is not None:
            queryset = Card.objects.filter(card_name__icontains=name)
        if type is not None:
            queryset = Card.objects.filter(type_line__icontains=type)

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])

        serializer = CardSerializer(queryset[:10], many=True)
        
        return Response(serializer.data)

    
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
        if name is not None:
            queryset = Deck.objects.filter(name__icontains=name)
        if user_id is not None:
            queryset = Deck.objects.filter(user_id=user_id)          
        
        # TODO - error handling
        queryset = queryset.filter(private=False)
        print(queryset)
        serializer = DeckSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        deck_data = JSONParser().parse(request)
        deck_serializer = DeckSerializer(data=deck_data)

        if deck_serializer.is_valid():
            deck_serializer.save()
            return JsonResponse(deck_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(deck_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        deck_id = request.query_params.get('id')
        Deck.objects.all().filter(id=deck_id).delete()
        # TODO - error handling
        return JsonResponse({'message': 'Deck was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    


class CardsInDeckView(APIView):
    #authentication_classes = [BasicAuthentication]
    #permission_classes = [IsAuthenticatedOrReadOnly] # TODO - tylko dany użytkownik


    def get(self, request):
        queryset = CardsInDeck.objects.none()

        deck_id = request.query_params.get('deck_id')
        
        # TODO - Django shortcut, error handling
        if deck_id is not None:
            #Checking if chosen deck is public
            deck = Deck.objects.filter(id=deck_id).filter(private=False)
            if deck.exists():
                queryset = CardsInDeck.objects.filter(deck_id=deck_id)

        if not queryset.exists():
            return Response({}, status=status.HTTP_200_OK)
      
        serializer = CardsInDeckSerializer(queryset, many=True)
        return Response(serializer.data)


    def post(self, request):
        card_data = JSONParser().parse(request)
        card_serializer = CardsInDeckSerializer(data=card_data)

        if card_serializer.is_valid():
            card_serializer.save()
            return JsonResponse(card_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(card_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        card_id = request.query_params.get('card_id')
        CardsInDeck.objects.all().filter(id=card_id).delete()
        # TODO - error handling
        return JsonResponse({'message': 'Deck was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
