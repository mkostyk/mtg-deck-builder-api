from django.urls import include, path, re_path
from rest_framework import routers
from knox import views as knox_views
from . import views
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', views.LoginView.as_view(), name='knox_login'),
    path('auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    
    path('cards/', views.CardView.as_view()),
    path('decks/', views.DeckView.as_view()),
    path('cardsInDeck/', views.CardsInDeckView.as_view()),
    path('prices/', views.PricesView.as_view()),
    path('legalities/', views.LegalitiesView.as_view()),
    path('images/', views.ImagesView.as_view()),
    path('tags/', views.DeckTagView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]