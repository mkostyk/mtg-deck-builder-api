from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import PricesSerializer
from ..models import Prices
from ..utils import PAGE_SIZE

class PricesView(APIView):
    card_id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)
    less_than_param = openapi.Parameter('less_than', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER)
    more_than_param = openapi.Parameter('more_than', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER)

    @swagger_auto_schema(manual_parameters=[card_id_param, less_than_param, more_than_param], operation_description="Get prices from the database",
    responses={200: PricesSerializer(many=True), 400: "Bad request: missing query parameters"})
    def get(self, request):
        queryset = Prices.objects.all()

        card_id = request.query_params.get('id')
        less_than = request.query_params.get('less_than')
        more_than = request.query_params.get('more_than')

        if card_id is None and less_than is None and more_than is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if card_id is not None:
            queryset = queryset.filter(card_id=card_id)
        if less_than is not None:
            queryset = queryset.filter(usd__lte=less_than)
        if more_than is not None:
            queryset = queryset.filter(usd__gte=more_than)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)
            
        serializer = PricesSerializer(queryset[:PAGE_SIZE], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def as_view():
    return PricesView.as_view()