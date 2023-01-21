from django.db.models import Q
from .models import Deck

PAGE_SIZE = 12

def get_deck_from_id(user, deck_id):
    if not user.is_anonymous:
        return Deck.objects.get(Q(id = deck_id) & (Q(private = False) | Q(author = user)))
    else:
        return Deck.objects.get(Q(id = deck_id) & Q(private = False))


def get_my_decks(user):
    if not user.is_anonymous:
        return Deck.objects.filter(Q(author = user))
    else:
        return Deck.objects.none()


def get_page(page):
    if page is None:
        page = 1
    else:
        page = int(page)
    return page