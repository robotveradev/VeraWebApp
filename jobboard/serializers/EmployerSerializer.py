from rest_framework import serializers

from users.models import Member


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', 'companies', 'full_name', 'tax_number', 'contract_address')
