from django.db import models

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