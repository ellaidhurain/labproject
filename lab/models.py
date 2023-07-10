from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.validators import FileExtensionValidator

# AbstractUser is used to create custom user model. 
# This is for user creation,registered user data is stored in this model(table)
# based on the group selected by user , user will be added to that group. 

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('C', 'Customer'),
        ('S', 'Supplier'),
        ('L', 'Laboratory'),
    )
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES)

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # OneToOneField -This ensures that each user has a unique profile.
    # Once user is created we need to add supplier user to Supplier table.
    # we can query Supplier based on the group name 
        
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Laboratory(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
# each SupplierForm will have a foreign key relationship with the corresponding Laboratory object. You can retrieve all the supplier forms associated with a specific laboratory by querying the SupplierForm
class SupplierForm(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, null=True) # one lab can have many supplier
    sub_name = models.CharField(max_length=100, blank=False)
    sub_address = models.CharField(max_length=100, blank=False)
    sub_proof = models.FileField(upload_to='proof/', blank=False,validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg','webp','png'])])
    product_name = models.CharField(max_length=100,blank=False,)
    product_image = models.FileField(upload_to='products/',blank=False,validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg','webp','png'])])
    certificate_image = models.FileField(upload_to='certificates/',blank=False,validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg','webp','png'])])
    
    accreditation_image =  models.FileField(upload_to='certificates/',blank=False,validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg','webp','png'])])
    agency_name = models.CharField(max_length=100, blank=False)
    accreditation_id = models.CharField(max_length=100, blank=False)
    ACCREDITATION_AGENCY_CHOICES = (
        ('startupindia','startupindia'),
        ('asme','asme'),
    ),
    
    accreditation_name=models.CharField(max_length=100,choices=ACCREDITATION_AGENCY_CHOICES, blank=False),
    accreditation_active_status = models.BooleanField(max_length=10, default=False)
    
    # these two field is verified by lab 
    test_result_image = models.FileField(upload_to='result/',blank=True,validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg','webp','png'])])
    STATUS_CHOICES = (
        ('P','Pending'),
        ('V','Verified'),
        ('R','Rejected'),  
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
 


