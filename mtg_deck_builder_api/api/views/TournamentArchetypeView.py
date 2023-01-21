from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import TournamentArchetypeSerializer
from ..models import TournamentArchetype, TournamentDeck
from ..permissions import IsStaffOrReadOnly


class TournamentArchetypeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrReadOnly]

    archetype_name_param = openapi.Parameter('archetype', openapi.IN_QUERY, description="Archetype name", type=openapi.TYPE_STRING)
    archetype_id_param = openapi.Parameter('archetype_id', openapi.IN_QUERY, description="Archetype id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[archetype_name_param, archetype_id_param],
    operation_description="Get tournament archetypes from the database",
    responses={200: TournamentArchetypeSerializer(many=True), 400: "Bad request: missing query parameters"})
    def get(self, request):
        archetype_name = request.query_params.get('archetype')
        archetype_id = request.query_params.get('archetype_id')
        queryset = TournamentArchetype.objects.all()

        if archetype_id is None and archetype_name is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if archetype_name is not None:
            queryset = queryset.filter(name=archetype_name)
        if archetype_id is not None:
            queryset = queryset.filter(id=archetype_id)

        if not queryset.exists():
            return Response({"message" : "Not found: chosen archetype does not exist"}, 
                              status=status.HTTP_404_NOT_FOUND)

        serializer = TournamentArchetypeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=TournamentArchetypeSerializer(), operation_description="Add tournament archetype to the database. Available only for admins.",
    responses={201: TournamentArchetypeSerializer, 400: "Bad request: missing query parameters"})    
    def post(self, request):
        tournament_archetype_data = JSONParser().parse(request)
        tournament_archetype_serializer = TournamentArchetypeSerializer(data=tournament_archetype_data)

        try:
            deck = TournamentDeck.objects.get(id=tournament_archetype_data['example_deck_id'])
        except TournamentDeck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if tournament_archetype_serializer.is_valid():
            print(tournament_archetype_serializer)
            tournament_archetype_serializer.save(example_deck=deck)
            return Response(tournament_archetype_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message" : "Bad request: data is not valid"}, 
                              status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(manual_parameters=[archetype_id_param], operation_description="Delete tournament archetype from the database",
    responses={200: "OK", 400: "Bad request: missing query parameters"})
    def delete(self, request):
        archetype_id = request.query_params.get('archetype_id')

        if archetype_id is not None:
            TournamentArchetype.objects.filter(id=archetype_id).delete()
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)


def as_view():
    return TournamentArchetypeView.as_view()