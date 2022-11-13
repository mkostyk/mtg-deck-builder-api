from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('cards/', views.CardView.as_view()),
    path('decks/', views.DeckView.as_view()),
    path('cardsInDeck/', views.CardsInDeckView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]