from django.db.models import Sum
from api.models import AmountOfIngredient
from django.http import HttpResponse


def download_shopping_cart(self, request):
    text = 'Ваш список покупок:\n\n'
    user = request.user
    ingredients = AmountOfIngredient.objects.filter(
        recipe__shopping_cart_recipe__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit')
    print(ingredients.__annotations__)
    ingredients.annotate(amount=Sum('amount'))

    for ingredient in ingredients:
        text += (f'{ingredient["ingredient__name"]}, '
                 f'{ingredient["ingredient__measurement_unit"]} -- '
                 f'{ingredient["amount"]} \n')

    response = HttpResponse(text, content_type='text/plain; charset=utf-8')
    filename = 'shopping_list.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
