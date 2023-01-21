from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import LegalitiesSerializer
from ..models import Legalities

class LegalitiesView(APIView):
    card_id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[card_id_param], operation_description="Get legalities from the database",
    responses={200: LegalitiesSerializer, 400: "Bad request: missing query parameters", 404: "Not found: chosen card does not exist"})
    def get(self, request):
        card_id = request.query_params.get('id')

        if card_id is not None:
            try:
                legalities = Legalities.objects.get(card_id=card_id)
            except Legalities.DoesNotExist:
                return Response({"message" : "Not found: chosen card does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
        serializer = LegalitiesSerializer(legalities, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

def as_view():
    return LegalitiesView.as_view()