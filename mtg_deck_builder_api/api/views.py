from django.shortcuts import render
from rest_framework import viewsets

from .serializers import CardSerializer
from .models import Card


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id')
        name = self.request.query_params.get('name')

        if id is not None:
            queryset = Card.objects.filter(id=id)
        elif name is not None:
            queryset = Card.objects.filter(card_name=name)

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])
        
        return queryset
    
    
