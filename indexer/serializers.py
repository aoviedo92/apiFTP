from rest_framework import serializers

from indexer.models import Files, Indexed


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files

class IndexedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indexed