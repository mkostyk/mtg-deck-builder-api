from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

# TODO - card faces, prices & legalities

class Card(models.Model):
    second_side = models.IntegerField(null=True) # TODO - foreign key to self
    scryfall_id = models.CharField(max_length = 40, null=True, blank=True)
    card_name = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    mana_cost = models.CharField(max_length = 50, null=True, blank=True)
    cmc = models.DecimalField(decimal_places = 1, max_digits = 10, null=True, blank=True)
    loyalty = models.CharField(max_length = 5, null=True, blank=True)
    power = models.CharField(max_length = 5, null=True, blank=True)
    toughness = models.CharField(max_length = 5, null=True, blank=True)
    type_line = models.TextField(null=True, blank=True)
    card_text = models.TextField(null=True, blank=True)
    color_identity = models.CharField(max_length = 20, null=True, blank=True)
    ruling_uri = models.CharField(max_length = 100, null=True, blank=True)
    rarity = models.CharField(max_length = 20, null=True, blank=True)
    flavor_text = models.TextField(null=True, blank=True)
    artist = models.CharField(max_length = 100, null=True, blank=True)


class Legalities(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, primary_key=True)
    standard = models.CharField(max_length=20)
    future = models.CharField(max_length=20)
    historic = models.CharField(max_length=20)
    gladiator = models.CharField(max_length=20)
    pioneer = models.CharField(max_length=20)
    explorer = models.CharField(max_length=20)
    modern = models.CharField(max_length=20)
    legacy = models.CharField(max_length=20)
    pauper = models.CharField(max_length=20)
    vintage = models.CharField(max_length=20)
    penny = models.CharField(max_length=20)
    commander = models.CharField(max_length=20)
    brawl = models.CharField(max_length=20)
    historicbrawl = models.CharField(max_length=20)
    alchemy = models.CharField(max_length=20)
    paupercommander = models.CharField(max_length=20)
    duel = models.CharField(max_length=20)
    oldschool = models.CharField(max_length=20)
    premodern = models.CharField(max_length=20)


class Prices(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, primary_key=True)
    usd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    usd_foil = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    usd_etched = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    eur = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    eur_foil = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tix = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    

class Images(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, primary_key=True)
    small = models.TextField(null=True)
    normal = models.TextField(null=True)
    large = models.TextField(null=True)
    png = models.TextField(null=True)
    art_crop = models.TextField(null=True)
    border_crop = models.TextField(null=True)


class Deck(models.Model):
    name = models.CharField(max_length = 1000)
    private = models.BooleanField()

    # If user is deleted models.CASCADE ensures that every reference
    # to it in Deck table will be deleted as well.
    author = models.ForeignKey(User, on_delete=models.CASCADE)

#Users are built in

class CardsInDeck(models.Model): # TODO - można to przerobić na ManyToManyField
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)


class DeckTag(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    tag = models.CharField(max_length = 100)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['deck', 'tag'], name='unique_tag') # TODO - lowercase/uppercase traktować tak samo?
        ]