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
        
class CardResultSerializer(CardSerializer):
    card_count = serializers.IntegerField()
    decks_count = serializers.IntegerField()

    class Meta:
        model = Card
        fields = CardSerializer.Meta.fields + ('card_count', 'decks_count')

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
    normal = serializers.CharField(max_length=200)
    large = serializers.CharField(max_length=200)
    png = serializers.CharField(max_length=200)
    art_crop = serializers.CharField(max_length=200)
    border_crop = serializers.CharField(max_length=200)

    class Meta:
        model = Images
        fields = ("card_id", "small", "normal", "large", "png", "art_crop", "border_crop")


class DeckTagSerializer(serializers.HyperlinkedModelSerializer):
    deck_id = serializers.IntegerField()
    tag = serializers.CharField(max_length = 1000)

    class Meta:
        model = DeckTag
        fields = ('deck_id', 'tag')


class DeckPostRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ('name', 'private', 'format')


class DeckSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length = 1000)
    format = serializers.CharField(max_length = 100)
    private = serializers.BooleanField()

    class Meta:
        model = Deck
        fields = ('id', 'name', 'private', 'format', 'last_update', 'votes', 'author')


class TournamentDeckSerializer(serializers.HyperlinkedModelSerializer):
    deck_id = serializers.IntegerField()
    tournament_format = serializers.CharField(max_length = 1000)
    player = serializers.CharField(max_length = 1000)

    class Meta:
        model = TournamentDeck
        fields = ('id', 'deck_id', 'tournament_format', 'player')


class TournamentArchetypeSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(max_length = 1000)
    popularity = serializers.DecimalField(max_digits=3, decimal_places=1)
    example_deck_id = serializers.IntegerField()
    format = serializers.CharField(max_length = 100)

    class Meta:
        model = TournamentArchetype
        fields = ('id', 'name', 'popularity', 'example_deck_id', 'format')


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


class UserWithTokenSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ('user', 'token')


class ResponseTokenSerializer(serializers.Serializer):
    expiry = serializers.DateTimeField()
    token = serializers.CharField()

    class Meta:
        fields = ('expiry', 'token')

class SideboardSerializer(serializers.HyperlinkedModelSerializer):
    deck_id = serializers.IntegerField()
    card_id = serializers.IntegerField()

    class Meta:
        model = Sideboard
        fields = ('id', 'deck_id', 'card_id')

class VoteSerializer(serializers.HyperlinkedModelSerializer):
    deck_id = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        model = Vote
        fields = ('id', 'deck_id', 'user_id', 'value')