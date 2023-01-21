from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import DeckTagSerializer
from ..models import DeckTag, Deck
from ..utils import *

class DeckTagView(APIView):    
    authentication_classes = [TokenAuthentication]

    deck_id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)
    tag_param = openapi.Parameter('tag', openapi.IN_QUERY, description="Tag", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[deck_id_param, tag_param], operation_description="Get tags from the database",
    responses={200: DeckTagSerializer(many=True), 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist"})
    def get(self, request):
        deck_id = request.query_params.get('id')
        tag = request.query_params.get('tag')

        if deck_id is None and tag is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if deck_id is not None:
            try:
                deck = get_my_decks(request.user).get(id=deck_id)
                tags = DeckTag.objects.filter(deck=deck)
            except Deck.DoesNotExist:
                return Response({"message" : "Not found: chosen deck does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        elif tag is not None:
            tags = DeckTag.objects.filter(tag=tag)
            for result_tag in tags:
                if (result_tag.deck.author != request.user) and result_tag.deck.private:
                    tags = tags.exclude(deck=result_tag.deck)
        else:
            return Response({"message" : "Bad request: missing query parameters"}, status=status.HTTP_400_BAD_REQUEST) # TODO

        serializer = DeckTagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(request_body=DeckTagSerializer, operation_description="Add tag to the deck",
    responses={201: DeckTagSerializer, 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or you are not this deck's author"})
    def post(self, request):
        tag_data = JSONParser().parse(request)
        tag_serializer = DeckTagSerializer(data=tag_data)

        # Checking if we are trying to add to our own deck.
        try:
            deck = get_my_decks(request.user).get(id=tag_data['deck'])
            tag = tag_data['tag']
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or you are not this deck's author"},
                            status=status.HTTP_404_NOT_FOUND)

        if tag_serializer.is_valid():
            tag_serializer.save(deck=deck, tag=tag) # TODO - chyba można bez argumentów?
            return Response(tag_serializer.data, status=status.HTTP_201_CREATED) 

        return Response(tag_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(request_body=DeckTagSerializer, operation_description="Delete tag from the deck", 
    responses={200: "OK", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or you are not this deck's author"})
    def delete(self, request):
        deck_id = request.query_params.get('deck_id')
        tag = request.query_params.get('tag')

        try:
            deck = get_my_decks(request.user).get(id=deck_id)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

        if tag is None:
            # Delete all tags from deck.
            DeckTag.objects.filter(deck=deck).delete()
        else:
            # Delete specific tag from deck.
            DeckTag.objects.filter(deck=deck, tag=tag).delete()

        return Response({}, status=status.HTTP_200_OK)

def as_view():
    return DeckTagView.as_view()