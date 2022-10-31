from rest_framework import serializers

from .models import Card, Deck, CardsInDeck

class CardSerializer(serializers.HyperlinkedModelSerializer):
    scryfall_id = serializers.CharField(max_length = 40)
    card_name = serializers.CharField(max_length = 1000)
    card_faces = serializers.CharField(max_length = 1000) #TODO
    keywords = serializers.CharField(max_length = 1000)
    image_uri = serializers.CharField(max_length = 100)
    mana_cost = serializers.CharField(max_length = 50)
    cmc = serializers.DecimalField(decimal_places = 1, max_digits = 10)
    loyalty = serializers.CharField(max_length = 5)
    power = serializers.CharField(max_length = 5)
    toughness = serializers.CharField(max_length = 5)
    type_line = serializers.CharField(max_length = 1000)
    card_text = serializers.CharField(max_length = 1000)
    color_identity = serializers.CharField(max_length = 20)
    legalities = serializers.JSONField()
    rulings_uri = serializers.CharField(max_length = 100)
    rarity = serializers.CharField(max_length = 20)
    flavor_text = serializers.CharField(max_length = 1000)
    artist = serializers.CharField(max_length = 100)
    edhrec_rank = serializers.IntegerField()
    prices = serializers.JSONField()

    class Meta:
        model = Card
        fields = ('id', 'scryfall_id', 'card_name', 'card_faces', 'keywords',
                  'image_uri', 'mana_cost', 'cmc', 'loyalty', 'power', 
                  'toughness', 'type_line', 'card_text', 'color_identity',
                  'legalities', 'rulings_uri', 'rarity', 'flavor_text',
                  'artist', 'edhrec_rank', 'prices')

class DeckSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(max_length = 1000)
    user_id = serializers.IntegerField()
    private = serializers.BooleanField()

    class Meta:
        model = Deck
        fields = ('id', 'name', 'user_id', 'private')


class CardsInDeckSerializer(serializers.HyperlinkedModelSerializer):
    deck_id = serializers.IntegerField()
    card_id = serializers.IntegerField()

    class Meta:
        model = CardsInDeck
        fields = ('id', 'deck_id', 'card_id')