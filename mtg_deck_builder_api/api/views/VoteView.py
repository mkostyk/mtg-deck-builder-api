from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.auth import TokenAuthentication

from ..models import Deck, Vote
from ..utils import *
from ..serializers import VoteSerializer

class VoteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    # TODO: ten 200 response
    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get votes for a deck",
    responses={200: "{'votes': 1 }", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or is not public"})
    def get(self, request):
        deck_id = request.query_params.get('deck_id')
        print(deck_id)
        
        if deck_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        try:
            deck = get_deck_from_id(request.user, deck_id)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or is not public"},
                            status=status.HTTP_404_NOT_FOUND)

        votes = Deck.objects.get(id=deck_id).votes;
        return Response({"votes" : votes})


    @swagger_auto_schema(request_body=VoteSerializer, operation_description="Vote for a deck",
    responses={201: VoteSerializer, 400: "Bad request: wrong vote value or you have already voted for this deck"})
    def post(self, request):
        vote_data = JSONParser().parse(request)
        if vote_data['value'] not in [1, -1]:
            return Response({"message" : "Bad request: wrong vote value"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        deck_id = vote_data['deck_id']
        
        try :
            deck = get_deck_from_id(request.user, deck_id)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or is not public"},
                            status=status.HTTP_404_NOT_FOUND)

        vote_serializer = VoteSerializer(data=vote_data)
        if Vote.objects.filter(user=request.user, deck=deck_id).exists():
            return Response({"message" : "Bad request: you have already voted for this deck"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if vote_serializer.is_valid():
            vote_serializer.save(user=request.user)

            # Update deck votes value.
            Deck.objects.filter(id=deck_id).update(votes=deck.votes + int(vote_data['value']))
            return Response(vote_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vote_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Delete a vote",
    responses={204: "Vote deleted", 400: "Bad request: missing query parameters", 404: "Not found: vote does not exist"})
    def delete(self, request):
        deck_id = request.query_params.get('deck_id')
        if deck_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        try:
            vote = Vote.objects.get(user=request.user, deck=deck_id)
        except Vote.DoesNotExist:
            return Response({"message" : "Not found: vote does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

        # Update deck votes value.
        Deck.objects.filter(id=deck_id).update(votes=Deck.objects.get(id=deck_id).votes - int(vote.value))
        vote.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def as_view():
    return VoteView.as_view()