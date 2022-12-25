from django.contrib import admin
from .models import *

admin.site.register(Card)
admin.site.register(Deck)
admin.site.register(CardsInDeck)
admin.site.register(Legalities)
admin.site.register(Prices)
admin.site.register(Images)
admin.site.register(DeckTag)

# Register your models here.
