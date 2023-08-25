from django.db import models

class ZohoSignDocument(models.Model):
    document_name = models.CharField(max_length=100)
    signer_email = models.EmailField()
    role_name = models.CharField(max_length=50)
    # Add other fields as needed

    def __str__(self):
        return self.document_name
