from django.urls import path
from .views import (
    StripeIntentView,
    stripe_webhook,
    CancelView,
    SuccessView,
    PaymentTemplateView,
    CheckoutSessionView)

urlpatterns = [
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('', PaymentTemplateView.as_view(), name='landing-page'),
    path('create-checkout-session/<pk>/', CheckoutSessionView.as_view(), name='create-checkout-session')
]
