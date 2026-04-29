from rest_framework import serializers
from .models import GeneHerb, HerbIngredient

class GeneHerbSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneHerb
        fields = '__all__' # 自动把所有字段变成 JSON

class HerbIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = HerbIngredient
        fields = '__all__'