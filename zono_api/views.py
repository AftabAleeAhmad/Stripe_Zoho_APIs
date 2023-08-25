import requests
from django.conf import settings
from django.http import JsonResponse
def create_agreement(request):
       """
       Create an agreement using the provided request.

       Args:
              request: The request object containing the necessary information for creating the agreement.

       Returns:
              A JSON response containing the success status and the agreement ID if successful, or a JSON response containing the success status and the error message if unsuccessful.
       """
       # Set up the necessary headers
       headers = {
           "Authorization": f"Zoho-oauthtoken {settings.ZOHO_CLIENT_SECRET}",
           "Content-Type": "application/json"
        }

       # Set up the request payload with the required information for the agreement
       payload = {
            "templates": {
            "field_data": {
                "field_text_data": {},
                "field_boolean_data": {},
                "field_date_data": {
                    "Date - 1": '01 January 1970'
                },
                "field_radio_data": {}
            },
            "actions": [
                {
                    "recipient_name": "Owner",
                    "recipient_email": "Dealer@test.com",
                    "action_id": "348837000000028026",
                    "signing_order": 1,
                    "role": "Owner",
                    "verify_recipient": False,
                    "private_notes": ""
                }
            ],
            "notes": ""
    }
}
    
       # Make the API request to create the agreement
       response = requests.post("https://sign.zoho.com/api/v1/templates/348837000000028001/createdocument", headers=headers, json=payload)

       # Process the response
       if response.status_code == 201:
           agreement_id = response.json()["id"]
           return JsonResponse({"success": True, "agreement_id": agreement_id})

       return JsonResponse({"success": False, "error": response.text}, status=response.status_code)
