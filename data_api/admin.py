from django.contrib import admin
from .models import GeneHerb, HerbIngredient

@admin.register(GeneHerb)
class GeneHerbAdmin(admin.ModelAdmin):
    # 将你想要在后台显示的字段全部列入此元组
    list_display = (
        'herb_id', 
        'full_name', 
        'gene', 
        'pubmed_id', 
        'reference_title', 
        'grade', 
        'relationship', 
        'p_value', 
        'fdr_bh'
    )
    search_fields = ('herb_id', 'full_name', 'gene')

@admin.register(HerbIngredient)
class HerbIngredientAdmin(admin.ModelAdmin):
    list_display = ('gene', 'herb', 'ingredient_id', 'ingredient_name', 'ingredient_alias_name', 'molecular_formula')
    search_fields = ('herb', 'ingredient_name', 'ingredient_id')