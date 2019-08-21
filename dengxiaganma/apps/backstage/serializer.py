from rest_framework import serializers
from ..user import models

# 车品牌序列化
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarBrand
        fields = "__all__"
