from django.shortcuts import render
from rest_framework import viewsets

from .serializers import CardsInDeckSerializer, CardSerializer, DeckSerializer
from .models import Card, CardsInDeck, Deck


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer

    def get_queryset(self):
        queryset = CardsInDeck.objects.none()

        id = self.request.query_params.get('id')
        name = self.request.query_params.get('name')

        if id is not None:
            queryset = Card.objects.filter(id=id)
        elif name is not None:
            queryset = Card.objects.filter(card_name=name)

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])
        
        return queryset
    

class DeckViewSet(viewsets.ModelViewSet):
    serializer_class = DeckSerializer

    def get_queryset(self):
        queryset = CardsInDeck.objects.none()

        id = self.request.query_params.get('id')
        name = self.request.query_params.get('name')
        user_id = self.request.query_params.get('user_id')

        if id is not None:
            queryset = Deck.objects.filter(id=id)
        elif name is not None:
            queryset = Deck.objects.filter(name=name)
        elif user_id is not None:
            queryset = Deck.objects.filter(user_id=user_id)

        if queryset.exists():
            queryset.filter(private=False)
        
        return queryset



class CardsInDeckViewSet(viewsets.ModelViewSet):
    serializer_class = CardsInDeckSerializer

    def get_queryset(self):
        queryset = CardsInDeck.objects.none()

        deck_id = self.request.query_params.get('deck_id')
        
        if deck_id is not None:
            deck = Deck.objects.filter(id=deck_id).filter(private=False)
            if deck.exists():
                queryset = CardsInDeck.objects.filter(deck_id=deck_id)
                   
        return queryset
