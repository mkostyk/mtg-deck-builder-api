from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..utils import get_page, PAGE_SIZE, reverse_case_insensitive_contains as ricontains, or_filter_from_dict as or_filter
from ..models import Card, Legalities
from ..serializers import CardSerializer


class CardView(APIView):
    id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)
    name_param = openapi.Parameter('name', openapi.IN_QUERY, description="Card name", type=openapi.TYPE_STRING)
    exact_name_param = openapi.Parameter('exact_name', openapi.IN_QUERY, description="Card exact name", type=openapi.TYPE_STRING)
    type_param = openapi.Parameter('type', openapi.IN_QUERY, description="Card type", type=openapi.TYPE_STRING)
    page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1)
    color_identity_param = openapi.Parameter('color_identity', openapi.IN_QUERY, description="Card color identity", type=openapi.TYPE_STRING)
    exact_color_identity_param = openapi.Parameter('exact_color_identity', openapi.IN_QUERY, description="Card exact color identity", type=openapi.TYPE_STRING)
    format_name_param = openapi.Parameter('format_name', openapi.IN_QUERY, description="Format name", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[id_param, name_param, type_param, page_param, color_identity_param, exact_color_identity_param, format_name_param], operation_description="Get cards from the database",
    responses={200: CardSerializer(many=True), 400: "Bad request: missing/incorrect query parameters", 404: "Not found: try again with different parameters"})
    def get(self, request):
        queryset = Card.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')
        page = get_page(request.query_params.get('page'))
        exact_name = request.query_params.get('exact_name')
        color_identity = request.query_params.get('color_identity')
        exact_color_identity = request.query_params.get('exact_color_identity')
        format_name = request.query_params.get('format_name').lower()

        params_list = [id, name, type, exact_name, color_identity, exact_color_identity, format_name]

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
            queryset = queryset.filter(type_line__icontains=type)
        if color_identity is not None:
            queryset = ricontains(queryset, "color_identity", color_identity)
        if exact_color_identity is not None:
            queryset = queryset.filter(color_identity__iexact=exact_color_identity)
        if format_name is not None:
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

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])
        start = (page - 1) * PAGE_SIZE
        end = page * PAGE_SIZE

        serializer = CardSerializer(queryset[start:end], many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

def as_view():
    return CardView.as_view()