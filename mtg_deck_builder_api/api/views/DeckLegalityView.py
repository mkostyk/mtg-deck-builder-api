from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

from ..models import Deck, CardsInDeck, Legalities, Sideboard
from ..utils import *

magic_words = "a deck can have any nomber of cards named"

# TODO - singleton formats
def check_deck_basic_legality(deck):
    cards = CardsInDeck.objects.all().filter(deck=deck)
    sideboard = Sideboard.objects.all().filter(deck=deck)

    if cards.count() < 60 or sideboard.count() > 15:
        return False

    format = deck.format
    checkedCards = {}

    for deckCard in cards:
        card = deckCard.card
        lower_card_text = card.card_text.lower()

        legalities = Legalities.objects.get(card_id=card)
        legality = getattr(legalities, format)

        if not legality in ["legal", "restricted"]:
            return False

        # skip basic lands and cards with magic words
        if card.card_name in BASIC_LANDS or lower_card_text.find(magic_words):
            continue
        
        checkedCards[card] += 1
        if legality == "restricted" and checkedCards[card] > 1:
            return False

        if legality == "legal" and checkedCards[card] > 4:
            return False

    return True


class DeckLegalityView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get deck legality",
    responses={200: "TODO", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or is not public"})
    def get(self, request):
        deck_id = request.query_params.get('deck_id')

        if deck_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        try:
            deck = get_deck_from_id(request.user, deck_id)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or is not public"},
                            status=status.HTTP_404_NOT_FOUND)   
        

        return Response({"legal" : check_deck_basic_legality(deck)}, status=status.HTTP_200_OK)

def as_view():
    return DeckLegalityView.as_view()