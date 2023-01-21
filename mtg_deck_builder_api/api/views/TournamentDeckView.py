from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import TournamentDeckSerializer
from ..models import TournamentDeck, Deck
from ..permissions import IsStaffOrReadOnly


class TournamentDeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get tournament decks from the database",
    responses={200: TournamentDeckSerializer(many=True), 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist"})
    def get(self, request):
        tournament_deck_id = request.query_params.get('deck_id')

        if tournament_deck_id is not None:
            try:
                queryset = TournamentDeck.objects.filter(id=tournament_deck_id)
            except Deck.DoesNotExist:
                return Response({"message" : "Not found: chosen deck does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        serializer = TournamentDeckSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(request_body=TournamentDeckSerializer(), operation_description="Add deck as a tournament deck",
    responses={201: TournamentDeckSerializer, 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or you are not this deck's author"})
    def post(self, request):
        tournament_deck_data = JSONParser().parse(request)
        tournament_deck_serializer = TournamentDeckSerializer(data=tournament_deck_data)

        try:
            deck = Deck.objects.get(id=tournament_deck_data['deck_id'])
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or you are not this deck's author"},
                            status=status.HTTP_404_NOT_FOUND)

        if tournament_deck_serializer.is_valid():
            tournament_deck_serializer.save(deck=deck)
            return Response(tournament_deck_serializer.data, status=status.HTTP_201_CREATED)


    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Delete tournament deck from the database",
    responses={200: "OK", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist"})
    def delete(self, request):
        deck_id = request.query_params.get('deck_id')

        if deck_id is not None:
            TournamentDeck.objects.filter(id=deck_id).delete()
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)


def as_view():
    return TournamentDeckView.as_view()

