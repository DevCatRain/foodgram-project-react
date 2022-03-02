from rest_framework import serializers

MIN_COOK_TIME = 'Время приготовления блюда должно быть не менее одной минуты'


def min_cooking_time(value):
    if value < 1:
        raise serializers.ValidationError({'cooking_time': MIN_COOK_TIME})
