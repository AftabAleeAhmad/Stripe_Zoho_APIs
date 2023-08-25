from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
import json
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = "success_template.html"


class CancelView(TemplateView):
    template_name = "cancel_template.html"


class PaymentTemplateView(TemplateView):
    template_name = "payment_template.html"

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for the view.

        Parameters:
            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The updated context data.
        """
        product = Product.objects.get(name="sample product")
        context = super(PaymentTemplateView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
        })
        return context


class CheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        """
        Creates a new checkout session for the specified product.

        Parameters:
            request (HttpRequest): The HTTP request object.
            args (list): Additional positional arguments.
            kwargs (dict): Additional keyword arguments.

        Returns:
            HttpResponse: A redirect to the checkout session URL.

        Raises:
            Exception: If an error occurs during the session creation.

        Example Usage:
            post(request, *args, **kwargs)
        """
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        try:
            checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': product.price,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        except Exception as e:
            return str(e)
        metadata={
                "product_id": product.id
            },

        return redirect(checkout_session.url, code=303)
        # return JsonResponse({
        #     'id': checkout_session.id
        # })


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: The HTTP response object with a status code of 200 if the webhook event is successfully handled.
        
    Raises:
        ValueError: If the payload is invalid.
        stripe.error.SignatureVerificationError: If the signature is invalid.
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="alee@test.com"
        )

        # TODO - decide whether you want to send the file or the URL
    
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject=f"congratulations! You bought {product.name} Successfull",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="alee@test.com"
        )

    return HttpResponse(status=200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        """
        Processes a POST request to create a PaymentIntent for a product.

        Parameters:
            request (Request): The HTTP request object.
            args (tuple): Positional arguments.
            kwargs (dict): Keyword arguments.

        Returns:
            JsonResponse: A JSON response containing the client secret if successful, or an error message if an exception occurs.
        """
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            intent = stripe.PaymentIntent.create(
                amount=product.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "product_id": product.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })