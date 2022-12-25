from django.urls import include, path
from rest_framework import routers
from knox import views as knox_views
from . import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view(), name='knox_login'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    
    path('cards/', views.CardView.as_view()),
    path('decks/', views.DeckView.as_view()),
    path('cardsInDeck/', views.CardsInDeckView.as_view()),
    path('prices/', views.PricesView.as_view()),
    path('legalities/', views.LegalitiesView.as_view()),
    path('images/', views.ImagesView.as_view()),
    path('tags/', views.DeckTagView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]