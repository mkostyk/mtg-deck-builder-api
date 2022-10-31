from django.contrib import admin
from .models import Card, Deck, CardsInDeck

admin.site.register(Card)
admin.site.register(Deck)
admin.site.register(CardsInDeck)

# Register your models here.
