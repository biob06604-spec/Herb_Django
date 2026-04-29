from django.core.exceptions import ObjectDoesNotExist
from data_api.models import HerbIngredient
from data_api.services.herb_lookup_service import resolve_herb_to_id


def serialize_herb_ingredient(obj: HerbIngredient) -> dict:
    return {
        "gene": obj.gene,
        "herb": obj.herb,
        "ingredient_id": obj.ingredient_id,
        "ingredient_name": obj.ingredient_name,
        "ingredient_alias_name": obj.ingredient_alias_name,
        "molecular_formula": obj.molecular_formula,
    }


def search_herb_ingredients_by_herb(herb: str, limit: int = 20) -> list[dict]:
    """
    支持用户输入 herb_id、中文名、英文名、别名
    先解析 herb_id，再查成分
    """
    resolved = resolve_herb_to_id(herb)

    if resolved:
        herb_id = resolved["herb_id"]

        # 优先按 herb_id 查
        queryset = HerbIngredient.objects.filter(herb__icontains=herb_id)[:limit]
        results = [serialize_herb_ingredient(obj) for obj in queryset]

        if results:
            return results

    # 如果 herb_id 没解析到，或按 herb_id 查不到，再回退到原始模糊匹配
    queryset = HerbIngredient.objects.filter(herb__icontains=herb)[:limit]
    return [serialize_herb_ingredient(obj) for obj in queryset]


def search_herb_ingredients_by_gene(gene: str, limit: int = 20) -> list[dict]:
    queryset = HerbIngredient.objects.filter(gene__icontains=gene)[:limit]
    return [serialize_herb_ingredient(obj) for obj in queryset]


def get_herb_ingredient_by_name(ingredient_name: str) -> dict:
    try:
        obj = HerbIngredient.objects.get(ingredient_name=ingredient_name)
        return serialize_herb_ingredient(obj)
    except ObjectDoesNotExist:
        return {"error": f"HerbIngredient with ingredient_name={ingredient_name} not found"}