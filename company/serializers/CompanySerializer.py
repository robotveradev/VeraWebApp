from rest_framework import serializers

from company.models import Company
from company.serializers.OfficeSerializer import OfficeSerializer
from vacancy.serializers.VacancySerializer import VacancySerializer


class CompanySerializer(serializers.ModelSerializer):
    vacancies = VacancySerializer(many=True, read_only=True)
    offices = OfficeSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'tax_number', 'legal_address', 'phone', 'email', 'verified', 'vacancies', 'offices')
