from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    scryfall_id = models.CharField(max_length = 40, null=True, blank=True)
    card_name = models.TextField(null=True, blank=True)
    card_faces = models.TextField(null=True, blank=True) #TODO
    keywords = models.TextField(null=True, blank=True)
    image_uri = models.CharField(max_length = 100, null=True, blank=True)
    mana_cost = models.CharField(max_length = 50, null=True, blank=True)
    cmc = models.DecimalField(decimal_places = 1, max_digits = 10, null=True, blank=True)
    loyalty = models.CharField(max_length = 5, null=True, blank=True)
    power = models.CharField(max_length = 5, null=True, blank=True)
    toughness = models.CharField(max_length = 5, null=True, blank=True)
    type_line = models.TextField(null=True, blank=True)
    card_text = models.TextField(null=True, blank=True)
    color_identity = models.CharField(max_length = 20, null=True, blank=True)
    legalities = models.JSONField(null=True, blank=True)
    rulings_uri = models.CharField(max_length = 100, null=True, blank=True)
    rarity = models.CharField(max_length = 20, null=True, blank=True)
    flavor_text = models.TextField(null=True, blank=True)
    artist = models.CharField(max_length = 100, null=True, blank=True)
    edhrec_rank = models.IntegerField(null=True, blank=True)
    prices = models.JSONField(null=True, blank=True)

class Deck(models.Model):
    name = models.CharField(max_length = 1000)
    user_id = models.PositiveIntegerField() # TODO - wywalić
    private = models.BooleanField()

    # If user is deleted models.CASCADE ensures that every reference
    # to it in Deck table will be deleted as well.
    author = models.ForeignKey(User, on_delete=models.CASCADE)

#Users are built in

class CardsInDeck(models.Model):
    deck_id = models.PositiveIntegerField()
    card_id = models.PositiveIntegerField()