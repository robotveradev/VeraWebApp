from rest_framework import serializers

from jobboard.models import Employer


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ('id', 'user', 'companies', 'full_name', 'tax_number', 'contract_address')
