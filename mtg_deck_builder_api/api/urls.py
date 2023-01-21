from django.urls import include, path, re_path
from rest_framework import routers
from knox import views as knox_views
from . import views_test
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

import views

schema_view = get_schema_view(
   openapi.Info(
      title="MTG Deck Builder API",
      default_version='v0.1',
      description='This is an API for Magic The Gathering Deck Builder. ' +
      'IMPORTANT: If you want to authenticate yourself on this page you need to send `Token <actual token>` in Authentication header. '+
      'For example: `"Authentication": "Token a711295d4963fb28f01b4758afab4f4e82e0b226376e2c1584053007c2556108"`. You can get your token by logging in.',
      contact=openapi.Contact(email="m.kostyk22@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
   path('auth/register/', views_test.RegisterView.as_view()),
   path('auth/login/', views_test.LoginView.as_view(), name='knox_login'),
   path('auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
   path('auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    
   path('cards/', views_test.CardView.as_view()),
   path('decks/', views_test.DeckView.as_view()),
   path('cardsInDeck/', views_test.CardsInDeckView.as_view()),
   path('sideboard/', views_test.SideboardView.as_view()),
   path('prices/', views_test.PricesView.as_view()),
   path('legalities/', views_test.LegalitiesView.as_view()),
   path('images/', views_test.ImagesView.as_view()),
   path('tags/', views_test.DeckTagView.as_view()),
   path('tournamentDecks/', views_test.TournamentDeckView.as_view()),
   path('tournamentArchetypes/', views_test.TournamentArchetypeView.as_view()),
   path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

   path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]