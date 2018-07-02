from rest_framework import serializers

from company.serializers.CompanySerializer import CompanySerializer
from jobboard.models import Employer


class EmployerFullSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True)

    class Meta:
        model = Employer
        fields = ('id', 'user', 'companies', 'full_name', 'tax_number', 'contract_address')
