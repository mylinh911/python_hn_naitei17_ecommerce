from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'user_name': {'required': True},
            'email': {'required': True},
            'full_name': {'required': True},
            'address': {'required': True},
            'phone': {'required': True},
        }

    def validate_user_name(self, value):
        if self.instance:
            if Customer.objects.filter(user_name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"This user_name already exists."})
        else:
            if Customer.objects.filter(user_name=value).exists():
                raise serializers.ValidationError({"This user_name already exists."})
        return value
