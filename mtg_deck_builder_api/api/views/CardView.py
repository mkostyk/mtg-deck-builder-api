from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..utils import get_page, PAGE_SIZE, reverse_case_insensitive_contains as ricontains, \
or_filter_from_dict as or_filter, and_filter_from_dict as and_filter, count_card_occurrences
from ..models import Card, Legalities
from ..serializers import CardSerializer, CardResultSerializer


class CardView(APIView):
    # TODO - this should definitely be a body parameter cause it's a lot of data
    id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)
    name_param = openapi.Parameter('name', openapi.IN_QUERY, description="Card name", type=openapi.TYPE_STRING)
    exact_name_param = openapi.Parameter('exact_name', openapi.IN_QUERY, description="Card exact name", type=openapi.TYPE_STRING)
    type_param = openapi.Parameter('type', openapi.IN_QUERY, description="Card type", type=openapi.TYPE_STRING)
    page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1)
    color_identity_param = openapi.Parameter('color_identity', openapi.IN_QUERY, description="Card color identity", type=openapi.TYPE_STRING)
    exact_color_identity_param = openapi.Parameter('exact_color_identity', openapi.IN_QUERY, description="Card exact color identity", type=openapi.TYPE_STRING)
    format_name_param = openapi.Parameter('format_name', openapi.IN_QUERY, description="Format name", type=openapi.TYPE_STRING)
    exact_cmc = openapi.Parameter('exact_cmc', openapi.IN_QUERY, description="Exact converted mana cost", type=openapi.TYPE_INTEGER)
    rarity = openapi.Parameter('rarity', openapi.IN_QUERY, description="Card rarity", type=openapi.TYPE_STRING)
    artist = openapi.Parameter('artist', openapi.IN_QUERY, description="Card artist", type=openapi.TYPE_STRING)
    card_text = openapi.Parameter('card_text', openapi.IN_QUERY, description="Card text", type=openapi.TYPE_STRING)
    card_text_one_block = openapi.Parameter('card_text_one_block', openapi.IN_QUERY, description="Card text in one continuous block", type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        manual_parameters=[id_param, name_param, type_param, page_param, color_identity_param,\
                            exact_color_identity_param, format_name_param, exact_cmc, rarity,\
                            artist, card_text, card_text_one_block],
        operation_description="Get cards from the database",
        responses={200: CardResultSerializer(many=True), 
                   400: "Bad request: missing/incorrect query parameters",
                   404: "Not found: try again with different parameters"}
    )
    def get(self, request):
        queryset = Card.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')
        page = get_page(request.query_params.get('page'))
        exact_name = request.query_params.get('exact_name')
        color_identity = request.query_params.get('color_identity')
        exact_color_identity = request.query_params.get('exact_color_identity')
        format_name = request.query_params.get('format_name')
        exact_cmc = request.query_params.get('exact_cmc')
        rarity = request.query_params.get('rarity')
        artist = request.query_params.get('artist')
        card_text = request.query_params.get('card_text')
        card_text_one_block = request.query_params.get('card_text_one_block')

        params_list = [id, name, type, exact_name, color_identity, exact_color_identity, \
                        format_name, exact_cmc, rarity, artist, card_text, card_text_one_block]

        if not any(params_list) or page < 1:
            return Response({"message" : "Bad request: missing/incorrect query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if id is not None:
            queryset = queryset.filter(id=id)
        if name is not None:
            queryset = queryset.filter(card_name__icontains=name)
        if exact_name is not None:
            queryset = queryset.filter(card_name__iexact=exact_name)
        if type is not None:
            type_filter_dict = {"type_line__icontains": type.split(" ")}
            type_filter = and_filter(type_filter_dict)

            queryset = queryset.filter(type_filter)
        if color_identity is not None:
            queryset = ricontains(queryset, "color_identity", color_identity)
        if exact_color_identity is not None:
            queryset = queryset.filter(color_identity__iexact=exact_color_identity)
        if exact_cmc is not None:
            queryset = queryset.filter(cmc=exact_cmc)
        if rarity is not None:
            queryset = queryset.filter(rarity__iexact=rarity)
        if artist is not None:
            queryset = queryset.filter(artist__iexact=artist)

        if card_text is not None and card_text != "":
            filter_params = {"card_text__icontains": card_text.split(" ")}
            text_filter = and_filter(filter_params)
            
            queryset = queryset.filter(text_filter)

        if card_text_one_block is not None:           
            queryset = queryset.filter(card_text__icontains=card_text_one_block)

        if format_name is not None and format_name != "":
            # TODO - optymalizacja
            format_name = format_name.lower() # column name - has to be lowercase
            filter_params = {format_name: ['legal', 'restricted']}
            filter = or_filter(filter_params)
            format_queryset = Legalities.objects.filter(filter)

            cards_ids = []
            for e in format_queryset:
                cards_ids.append(e.card_id)

            queryset = queryset.filter(id__in=cards_ids)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)

        # TODO - sortowanie po popularności
        start = (page - 1) * PAGE_SIZE
        end = page * PAGE_SIZE
        queryset = queryset.order_by('card_name')
        
        serializer = CardSerializer(queryset[start:end], many=True)

        for card in serializer.data:
            counts = count_card_occurrences(card['id'])
            card['card_count'] = counts.get('card_count', 0)
            card['decks_count'] = counts.get('decks_count', 0)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

def as_view():
    return CardView.as_view()