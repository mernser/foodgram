from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view

from recipes.models import Recipie


@api_view(('GET',))
def short_link_redirect(request, short_link):
    recipe = get_object_or_404(Recipie, short_link=short_link)
    return redirect(request.build_absolute_uri(f'/recipes/{recipe.pk}'))
