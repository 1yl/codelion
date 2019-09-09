from rest_framework import serializers
from ..user import models

# 活动序列化
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields = "__all__"
