from django.db.models import Q
from .models import Deck
from django.db.models import F, Value, CharField

PAGE_SIZE = 12
FORMATS = ["Standard", "Alchemy", "Modern", "Legacy", "Vintage", "Commander", "Pauper", "Pioneer", "Explorer", "Brawl", "Historic", "Penny"]
BASIC_LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest"]

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

@staticmethod
def reverse_case_insensitive_contains(queryset, search_field_name: str, search_field_value: str):
    return queryset \
        .annotate(search_field=Value(search_field_value, output_field=CharField())) \
        .filter(search_field__icontains=F(search_field_name))


def or_filter_from_dict(filter_dict):
    my_filter = Q()

    for column in filter_dict:
        for item in filter_dict[column]:
            my_filter |= Q(**{column:item})

    return my_filter