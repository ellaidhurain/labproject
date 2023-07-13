from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import User, Supplier, SupplierForm, Laboratory, Customer
from django.core.exceptions import ValidationError
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'user_type', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user_type = validated_data['user_type']
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            user_type=user_type
        )

        if user_type == 'S':  # Supplier user
            supplier = Supplier.objects.create(user=user)
            
        if user_type == 'C':  # Supplier user
            supplier = Customer.objects.create(user=user)
        
        if user_type == 'L':  # Supplier user
            supplier = Laboratory.objects.create(user=user)
            
        return user

class SupplierFormSerializer(serializers.ModelSerializer):
    sub_proof_url = serializers.SerializerMethodField()
    product_image_url = serializers.SerializerMethodField()
    certificate_image_url = serializers.SerializerMethodField()
    accreditation_image_url = serializers.SerializerMethodField()
    test_result_image_url = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
   
    class Meta:
        model = SupplierForm
        fields = '__all__'
        
    def get_sub_proof_url(self, obj):
        if obj.sub_proof:
            return self._get_full_url(obj.sub_proof.url)
        return None
        
    def get_product_image_url(self, obj):
        if obj.product_image:
            return self._get_full_url(obj.product_image.url)
        return None
        
    def get_certificate_image_url(self, obj):
        if obj.certificate_image:
            return self._get_full_url(obj.certificate_image.url)
        return None
    
    def get_accreditation_image_url(self, obj):
        if obj.certificate_image:
            return self._get_full_url(obj.accreditation_image.url)
        return None
        
    def get_test_result_image_url(self, obj):
        if obj.test_result_image:
            return self._get_full_url(obj.test_result_image.url)
        return None
    
    def _get_full_url(self, relative_url):
        if not relative_url.startswith('http'):
            return f"{settings.BASE_URL.rstrip('/')}{relative_url}"
        return relative_url
    
    def get_customer(self, obj):
        customer = obj.customer
        return {
            "id": customer.id,
            "username": customer.username,  
        }
        
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class LaboratoryFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        
