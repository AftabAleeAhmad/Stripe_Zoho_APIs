from django.urls import path
from .views import create_agreement

urlpatterns = [
    path('create-agreement/', create_agreement, name='create_agreement'),
]
