from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import *


class CardSerializer(serializers.HyperlinkedModelSerializer):
    second_side = serializers.IntegerField()
    scryfall_id = serializers.CharField(max_length = 40)
    card_name = serializers.CharField(max_length = 1000)
    keywords = serializers.CharField(max_length = 1000)
    mana_cost = serializers.CharField(max_length = 50)
    cmc = serializers.DecimalField(decimal_places = 1, max_digits = 10)
    loyalty = serializers.CharField(max_length = 5)
    power = serializers.CharField(max_length = 5)
    toughness = serializers.CharField(max_length = 5)
    type_line = serializers.CharField(max_length = 1000)
    card_text = serializers.CharField(max_length = 1000)
    color_identity = serializers.CharField(max_length = 20)
    ruling_uri = serializers.CharField(max_length = 100)
    rarity = serializers.CharField(max_length = 20)
    flavor_text = serializers.CharField(max_length = 1000)
    artist = serializers.CharField(max_length = 100)

    class Meta:
        model = Card
        fields = ('id', 'second_side', 'scryfall_id', 'card_name', 'keywords', 'mana_cost', 
                  'cmc', 'loyalty', 'power', 'toughness', 'type_line',
                  'card_text', 'color_identity', 'ruling_uri', 'rarity',
                  'flavor_text', 'artist')

class LegalitiesSerializer(serializers.HyperlinkedModelSerializer):
    card_id = serializers.IntegerField()
    standard = serializers.CharField(max_length=20)
    future = serializers.CharField(max_length=20)
    historic = serializers.CharField(max_length=20)
    gladiator = serializers.CharField(max_length=20)
    pioneer = serializers.CharField(max_length=20)
    explorer = serializers.CharField(max_length=20)
    modern = serializers.CharField(max_length=20)
    legacy = serializers.CharField(max_length=20)
    pauper = serializers.CharField(max_length=20)
    vintage = serializers.CharField(max_length=20)
    penny = serializers.CharField(max_length=20)
    commander = serializers.CharField(max_length=20)
    brawl = serializers.CharField(max_length=20)
    historicbrawl = serializers.CharField(max_length=20)
    alchemy = serializers.CharField(max_length=20)
    paupercommander = serializers.CharField(max_length=20)
    duel = serializers.CharField(max_length=20)
    oldschool = serializers.CharField(max_length=20)
    premodern = serializers.CharField(max_length=20)

    class Meta:
        model = Legalities
        fields = ("card_id", "standard", "future", "historic", "gladiator", "pioneer",
                  "explorer", "modern", "legacy", "pauper", "vintage",
                  "penny", "commander", "brawl", "historicbrawl", "alchemy",
                  "paupercommander", "duel", "oldschool", "premodern")


class PricesSerializer(serializers.HyperlinkedModelSerializer):
    card_id = serializers.IntegerField()
    usd = serializers.DecimalField(max_digits=10, decimal_places=2)
    usd_foil = serializers.DecimalField(max_digits=10, decimal_places=2)
    usd_etched = serializers.DecimalField(max_digits=10, decimal_places=2)
    eur = serializers.DecimalField(max_digits=10, decimal_places=2)
    eur_foil = serializers.DecimalField(max_digits=10, decimal_places=2)
    tix = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Prices
        fields = ("card_id", "usd", "usd_foil", "usd_etched", "eur", "eur_foil", "tix")


class ImagesSerializer(serializers.HyperlinkedModelSerializer):
    card_id = serializers.IntegerField()
    small = serializers.CharField(max_length=200)
    medium = serializers.CharField(max_length=200)
    large = serializers.CharField(max_length=200)
    png = serializers.CharField(max_length=200)
    art_crop = serializers.CharField(max_length=200)
    border_crop = serializers.CharField(max_length=200)

    class Meta:
        model = Images
        fields = ("card_id", "small", "medium", "large", "png", "art_crop", "border_crop")


class DeckSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(max_length = 1000)
    private = serializers.BooleanField()

    class Meta:
        model = Deck
        fields = ('id', 'name', 'private')


class CardsInDeckSerializer(serializers.HyperlinkedModelSerializer):
    deck_id = serializers.IntegerField()
    card_id = serializers.IntegerField()

    class Meta:
        model = CardsInDeck
        fields = ('id', 'deck_id', 'card_id')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        return User.objects.create_user(validated_data['username'], 
                                        None,
                                        validated_data['password'])


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class AuthSerializer(serializers.Serializer):
    '''serializer for the user authentication object'''
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        
        if not user:
            msg = ('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return 