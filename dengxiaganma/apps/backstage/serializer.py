from rest_framework import serializers
from ..user import models

# 车品牌序列化
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarBrand
        fields = "__all__"

# 车系列序列化
class SeriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarSeries
        fields = "__all__"

# 车型号序列化
class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarModel
        fields = "__all__"