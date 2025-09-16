from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

from .views.label_trigger_view import LabelTriggerView
from .views.start_eventbus_engine import StartEventBusEngine
from .views.user_character_view import UserCharactersView
from .views.user_view import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth', obtain_auth_token, name='api_token_auth'),
    path('start-event-engine',StartEventBusEngine.as_view(),name='start-event-engine'),
    path('user-characters', UserCharactersView.as_view(), name="user-characters"),
    path('label-trigger',LabelTriggerView.as_view(),name='label-trigger'),

]