from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser 
from rest_framework.authtoken.serializers import AuthTokenSerializer

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from knox.models import AuthToken

from django.http import JsonResponse
from django.shortcuts import get_list_or_404 # TODO - use this
from django.contrib.auth import login
from django.db.models import Q

# docs stuff
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import *
from .models import *
# TODO - single objects instead of querysets
# TODO - many to many fields
# TODO - examples in docs, lepsze opisy
# TODO - request body w delete?

def get_deck_from_id(user, deck_id):
    if not user.is_anonymous:
        return Deck.objects.get(Q(id = deck_id) & (Q(private = False) | Q(author = user)))
    else:
        return Deck.objects.get(Q(id = deck_id) & Q(private = False))


def get_page(page):
    if page is None:
        page = 1
    else:
        page = int(page)
    return page


class RegisterView(APIView):
    @swagger_auto_schema(request_body=CreateUserSerializer, operation_description="Register a new user", 
    responses={201: UserWithTokenSerializer, 400: "Bad request: missing/incorrect data"})
    def post(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=serializer).data,
            "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_201_CREATED)


class LoginView(KnoxLoginView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=AuthTokenSerializer, operation_description="Login a user",
    responses={200: ResponseTokenSerializer, 400: "Bad request: missing/incorrect data"})

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']  # Nie wiem czemu to krzyczy bo działa
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class CardView(APIView):
    id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)
    name_param = openapi.Parameter('name', openapi.IN_QUERY, description="Card name", type=openapi.TYPE_STRING)
    type_param = openapi.Parameter('type', openapi.IN_QUERY, description="Card type", type=openapi.TYPE_STRING)
    page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1)

    @swagger_auto_schema(manual_parameters=[id_param, name_param, type_param, page_param], operation_description="Get cards from the database",
    responses={200: CardSerializer(many=True), 400: "Bad request: missing/incorrect query parameters", 404: "Not found: try again with different parameters"})
    def get(self, request):
        queryset = Card.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')
        page = get_page(request.query_params.get('page'))

        if id is None and name is None and type is None or page < 1:
            return Response({"message" : "Bad request: missing/incorrect query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        if id is not None:
            queryset = queryset.filter(id=id)
        if name is not None:
            queryset = queryset.filter(card_name__icontains=name)
        if type is not None:
            queryset = queryset.filter(type_line__icontains=type)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])
        start = (page - 1) * 10
        end = page * 10

        serializer = CardSerializer(queryset[start:end], many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class DeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)
    name_param = openapi.Parameter('name', openapi.IN_QUERY, description="Deck name", type=openapi.TYPE_STRING)
    user_id_param = openapi.Parameter('user_id', openapi.IN_QUERY, description="User id", type=openapi.TYPE_INTEGER)
    page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1)

    @swagger_auto_schema(manual_parameters=[id_param, name_param, user_id_param, page_param], operation_description="Get decks from the database",
    responses={200: DeckSerializer(many=True), 400: "Bad request: missing query parameters", 404: "Not found: user/deck does not exist or is private"})
    def get(self, request):
        queryset = Deck.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        user_id = request.query_params.get('user_id')
        page = get_page(request.query_params.get('page'))

        if id is None and name is None and user_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        # Filtering by query parameters
        if id is not None:
            queryset = queryset.filter(id=id)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if user_id is not None:
            try:
                if user_id == "-1": # why string?
                    user = request.user
                else:
                    user = User.objects.get(id=user_id)
                    
                queryset = queryset.filter(author=user)
            except User.DoesNotExist:
                return Response({"message" : "Not found: user does not exist"},
                                  status=status.HTTP_404_NOT_FOUND)

        # Filtering private decks
        if not request.user.is_anonymous:
            queryset = queryset.filter(Q(private=False) | Q(author=request.user))
        else:
            queryset = queryset.filter(private=False)

        if not queryset.exists():
            return Response({"message" : "Not found: deck does not exist or is private."},
                            status=status.HTTP_404_NOT_FOUND)

        start = (page - 1) * 10
        end = page * 10
        
        serializer = DeckSerializer(queryset[start:end], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(request_body=DeckSerializer(), operation_description="Create a new deck",
    responses={201: DeckSerializer, 400: "Bad request: missing query parameters"})
    def post(self, request):
        deck_data = JSONParser().parse(request)
        deck_serializer = DeckSerializer(data=deck_data)

        if deck_serializer.is_valid():
            deck_serializer.save(author=request.user)
            return Response(deck_serializer.data, status=status.HTTP_201_CREATED) 

        return Response(deck_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(manual_parameters=[id_param], operation_description="Delete a deck",
    responses={200: "OK", 400: "Bad request: missing query parameters", 404: "Not found: chosen deck does not exist or you are not its author"})
    def delete(self, request):
        deck_id = request.query_params.get('id') # TODO - (name, user_id) jako unique key

        if deck_id is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        # Checking if we are deck's author
        try:
            deck = Deck.objects.get(id=deck_id, author=request.user)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or you are not its author"},
                            status=status.HTTP_404_NOT_FOUND)

        deck.delete()

        # TODO - error handling
        return Response({}, status=status.HTTP_200_OK)
    


class CardsInDeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    deck_id_param = openapi.Parameter('deck_id', openapi.IN_QUERY, description="Deck id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Get cards in deck from the database",
    responses={200: CardsInDeckSerializer(many=True), 400: "Bad request: you have to specify deck id", 404: "Not found: chosen deck does not exist or is not public"})
    def get(self, request):
        queryset = CardsInDeck.objects.all()

        deck_id = request.query_params.get('deck_id')
        
        # TODO - Django shortcut, error handling
        if deck_id is not None: 
            #Checking if chosen deck is public.
            try:
                deck = get_deck_from_id(request.user, deck_id)
                    
                queryset = queryset.filter(deck = deck)
            except Deck.DoesNotExist:
                return Response({"message" : "Not found: chosen deck does not exist or is not public"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Bad request: you have to specify deck id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)
      
        serializer = CardsInDeckSerializer(queryset, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(request_body=CardsInDeckSerializer, operation_description="Add a card to a deck",
    responses={201: CardsInDeckSerializer, 400: "Bad request: missing query parameters", 404: "Not found: chosen card/deck does not exist or you are not this deck's author"})
    def post(self, request):
        card_data = JSONParser().parse(request)
        card_serializer = CardsInDeckSerializer(data=card_data)

        # Checking if we are trying to add to our own deck.
        try:
            deck = Deck.objects.get(id=card_data['deck_id'], author=request.user)
            card = Card.objects.get(id=card_data['card_id'])
        except Deck.DoesNotExist or Card.DoesNotExist:
            return Response({"message" : "Not found: chosen card/deck does not exist or you are not this deck's author"},
                            status=status.HTTP_404_NOT_FOUND)

        if card_serializer.is_valid():
            card_serializer.save(deck=deck, card=card)  # TODO - testing
            return Response(card_serializer.data, status=status.HTTP_201_CREATED) 

        return Response(card_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(manual_parameters=[deck_id_param], operation_description="Delete cards from a deck",
    responses={200: "OK", 400: "Bad request: missing query parameters or you are not this deck's author", 404: "Not found: chosen card does not exist"})
    def delete(self, request):
        card_id = request.query_params.get('card_id')
        
        try:
            deck = CardsInDeck.objects.get(id=card_id).deck
        except CardsInDeck.DoesNotExist:
            return Response({"message" : "Bad request: chosen card does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        if deck.author == request.user:
            if card_id is None:
                # Delete all cards from a deck
                CardsInDeck.objects.filter(deck=deck).delete()
            else:
                # Delete a single card from a deck
                CardsInDeck.objects.get(id=card_id).delete()
        else:
            return Response({"message" : "Bad request: you are not this deck's author"},
                            status=status.HTTP_400_BAD_REQUEST)

        # TODO - error handling
        return Response({}, status=status.HTTP_200_OK)


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
            queryset = queryset.filter(usd__lte=less_than) # TODO - other currencies
        if more_than is not None:
            queryset = queryset.filter(usd__gte=more_than)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)
            
        serializer = PricesSerializer(queryset[:10], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class ImagesView(APIView):
    card_id_param = openapi.Parameter('id', openapi.IN_QUERY, description="Card id", type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[card_id_param], operation_description="Get images from the database",
    responses={200: ImagesSerializer, 400: "Bad request: missing query parameters", 404: "Not found: chosen card does not exist"})
    def get(self, request):
        card_id = request.query_params.get('id')

        if card_id is not None:
            try:
                images = Images.objects.get(card_id=card_id)
            except Images.DoesNotExist:
                return Response({"message" : "Not found: chosen card does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Bad request: missing query parameters"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        serializer = ImagesSerializer(images, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class DeckTagView(APIView):
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
                deck = get_deck_from_id(request.user, deck_id)
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
            deck = Deck.objects.get(id=tag_data['deck_id'], author=request.user)
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
            deck = get_deck_from_id(request.user, deck_id)
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