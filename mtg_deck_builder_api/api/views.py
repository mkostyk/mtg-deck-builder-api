from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import get_list_or_404 # TODO - use this
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from knox.models import AuthToken
from django.db.models import Q

from .serializers import *
from .models import *
# TODO - error codes
# TODO - JsonResponse
# TODO - single objects instead of querysets
# TODO - many to many fields

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=serializer).data,
            "token": AuthToken.objects.create(user)[1]
        })


# TODO
class LoginView(KnoxLoginView):
    authentication_classes = [BasicAuthentication] #TODO


# TODO - error handling
class CardView(APIView):
    def get(self, request):
        queryset = Card.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')

        if id is None and name is None and type is None:
            return Response({"message" : "Bad request: missing query parameters"}, 
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

        serializer = CardSerializer(queryset[:10], many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class DeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        queryset = Deck.objects.all()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        user_id = request.query_params.get('user_id')

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
                user = User.objects.get(id=user_id)
                queryset = queryset.filter(author=user)
            except User.DoesNotExist:
                return Response({"message" : "Not found: user does not exist"},
                                  status=status.HTTP_404_NOT_FOUND)

        if not queryset.exists():
            return Response({"message" : "Not found: try again with different parameters"},
                            status=status.HTTP_404_NOT_FOUND)


        # Filtering private decks
        if not request.user.is_anonymous:
            queryset = queryset.filter(Q(private=False) | Q(author=request.user))
        else:
            queryset = queryset.filter(private=False)
        
        serializer = DeckSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        deck_data = JSONParser().parse(request)
        deck_serializer = DeckSerializer(data=deck_data)

        if deck_serializer.is_valid():
            deck_serializer.save(author=request.user)
        
            return Response(deck_serializer.data, status=status.HTTP_201_CREATED) 
        return Response(deck_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        deck_id = request.query_params.get('id')
        
        # Checking if we are deck's author
        try:
            deck = Deck.objects.get(id=deck_id, author=request.user)
        except Deck.DoesNotExist:
            return Response({"message" : "Not found: chosen deck does not exist or you are not its author"},
                            status=status.HTTP_404_NOT_FOUND)

        deck.delete()

        # TODO - error handling
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    


class CardsInDeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        queryset = CardsInDeck.objects.all()

        deck_id = request.query_params.get('deck_id')
        
        # TODO - Django shortcut, error handling
        if deck_id is not None: 
            #Checking if chosen deck is public.
            try:
                if not request.user.is_anonymous:
                    deck = Deck.objects.get(Q(id = deck_id) & (Q(private = False) | Q(author=request.user)))
                else:
                    deck = Deck.objects.get(Q(id = deck_id) & Q(private = False))
                    
                queryset = queryset.filter(deck = deck)
            except Deck.DoesNotExist:
                return Response({"message" : "Not found: chosen deck does not exist or is not public"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message" : "Bad request: you have to specify deck id"},
                            status=status.HTTP_400_BAD_REQUEST)
      
        serializer = CardsInDeckSerializer(queryset, many=True)
        return Response(serializer.data)


    def post(self, request):
        card_data = JSONParser().parse(request)
        card_serializer = CardsInDeckSerializer(data=card_data)

        print(card_data)

        # Checking if we are trying to add to our own deck.
        try:
            deck = Deck.objects.get(id=card_data['deck_id'], author=request.user)
            card = Card.objects.get(id=card_data['card_id'])
        except Deck.DoesNotExist or Card.DoesNotExist:
            return Response({"message" : "Not found: chosen card/deck does not exist or you are not this deck's author"},
                            status=status.HTTP_404_NOT_FOUND)

        if card_serializer.is_valid():
            card_serializer.deck = deck
            card_serializer.card = card # TODO - czy to by zadziałało na pałę?
            card_serializer.save()

            return Response(card_serializer.data, status=status.HTTP_201_CREATED) 

        return Response(card_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        card_id = request.query_params.get('card_id')
        
        try:
            deck = CardsInDeck.objects.get(id=card_id).deck
        except CardsInDeck.DoesNotExist:
            return Response({"message" : "Bad request: chosen card does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        if deck.author == request.user:
            CardsInDeck.objects.get(id=card_id).delete()
        else:
            return Response({"message" : "Bad request: you are not this deck's author"},
                            status=status.HTTP_400_BAD_REQUEST)

        # TODO - error handling
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class PricesView(APIView):
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
