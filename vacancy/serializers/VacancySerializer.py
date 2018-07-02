from rest_framework import serializers

from company.serializers.OfficeSerializer import OfficeSerializer
from jobboard.serializers.SpecialisationSerializer import SpecialisationSerializer
from jobboard.serializers.KeywordSerializer import KeywordSerializer
from vacancy.models import Vacancy
from vacancy.serializers.BusynessSerializer import BusynessSerializer
from vacancy.serializers.ScheduleSerializer import ScheduleSerializer


class VacancySerializer(serializers.ModelSerializer):
    company = serializers.CharField(source='company.name', read_only=True)
    company_id = serializers.CharField(source='company.id', read_only=True)
    specialisations = SpecialisationSerializer(many=True)
    keywords = KeywordSerializer(many=True)
    office = OfficeSerializer(many=True)
    busyness = BusynessSerializer(many=True)
    schedule = ScheduleSerializer(many=True)
    pipeline = serializers.HyperlinkedRelatedField(view_name='pipeline-detail', read_only=True)

    class Meta:
        model = Vacancy
        fields = ("id", "company", "company_id", "uuid", "title", "pipeline", "specialisations", "keywords",
                  "experience", "description", "requirement", "office", "salary_from", "salary_up_to",
                  "busyness", "schedule", "enabled", "published", "allowed_amount", "created_at", "updated_at")
