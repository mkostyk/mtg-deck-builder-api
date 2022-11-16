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
        queryset = CardsInDeck.objects.none()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        type = request.query_params.get('type')

        if id is not None:
            queryset = Card.objects.filter(id=id)
        if name is not None:
            queryset = Card.objects.filter(card_name__icontains=name)
        if type is not None:
            queryset = Card.objects.filter(type_line__icontains=type)

        # TODO - ogarnąć to
        #queryset = Card.objects.raw('SELECT * FROM cards WHERE card_name = %s', [name])

        serializer = CardSerializer(queryset[:10], many=True)
        
        return Response(serializer.data)

    
class DeckView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        queryset = CardsInDeck.objects.none()

        id = request.query_params.get('id')
        name = request.query_params.get('name')
        user_id = request.query_params.get('user_id')

        # Filtering by query parameters
        if id is not None:
            queryset = Deck.objects.filter(id=id)
        if name is not None:
            queryset = Deck.objects.filter(name__icontains=name)
        if user_id is not None:
            try:
                user = User.objects.get(id=user_id)
                queryset = Deck.objects.filter(author=user)
            except User.DoesNotExist:
                return Response({"message" : "Bad request: user ID is incorrect"},
                            status=status.HTTP_400_BAD_REQUEST)


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
        
            return JsonResponse(deck_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(deck_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        deck_id = request.query_params.get('id')
        
        # Checking if we are deck's author
        try:
            deck = Deck.objects.get(id=deck_id, author=request.user)
        except Deck.DoesNotExist:
            return Response({"message" : "Bad request: chosen deck does not exist or you are not its author"},
                            status=status.HTTP_400_BAD_REQUEST)

        deck.delete()

        # TODO - error handling
        return JsonResponse({'message': 'Deck was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    


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
                deck = Deck.objects.get(Q(id = deck_id) & (Q(private = False) | Q(author = request.user)))
                queryset = queryset.filter(deck_id = deck_id)
            except Deck.DoesNotExist:
                return Response({"message" : "Bad request: chosen deck does not exist or is not public"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Bad request: you have to specify deck id"},
                            status=status.HTTP_400_BAD_REQUEST)
      
        serializer = CardsInDeckSerializer(queryset, many=True)
        return Response(serializer.data)


    def post(self, request):
        card_data = JSONParser().parse(request)
        card_serializer = CardsInDeckSerializer(data=card_data)

        # Checking if we are trying to add to our own deck.
        try:
            deck = Deck.objects.get(id=card_data.deck_id, author=request.user)
        except Deck.DoesNotExist:
            return Response({"message" : "Bad request: chosen deck does not exist or you are not its author"},
                            status=status.HTTP_400_BAD_REQUEST)

        if card_serializer.is_valid() and deck.exists():
            card_serializer.save()
            return JsonResponse(card_serializer.data, status=status.HTTP_201_CREATED) 

        return JsonResponse(card_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        card_id = request.query_params.get('card_id')
        
        try:
            deck_id = CardsInDeck.object.get(id=card_id).deck_id
            deck = Deck.objects.get(id=deck_id, author=request.user)
        except Deck.DoesNotExist:
            return Response({"message" : "Bad request: chosen card does not exist or you are not its owner"},
                            status=status.HTTP_400_BAD_REQUEST)

        CardsInDeck.object.get(id=card_id).delete()

        # TODO - error handling
        return JsonResponse({'message': 'Card was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
