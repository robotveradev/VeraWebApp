from rest_framework import serializers

from company.models import Office


class OfficeSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True, source='address.address_line')

    class Meta:
        model = Office
        fields = ('id', 'address', 'main')
