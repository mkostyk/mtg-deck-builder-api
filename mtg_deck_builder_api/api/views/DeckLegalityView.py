from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

# TODO: implement this view
class DeckLegalityView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get deck legality",
    responses={200: "TODO", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or is not public"})
    def get(self, request):
        return Response({"message" : "TODO"}, status=status.HTTP_200_OK)

def as_view():
    return DeckLegalityView.as_view()