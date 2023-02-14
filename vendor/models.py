from django.db import models

from accounts.models import User, BaseModel


# Create your models here.
class Vendor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=200)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.vendor_name
