from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework import filters, viewsets

from .models import GeneHerb, HerbIngredient 
from .serializers import GeneHerbSerializer, HerbIngredientSerializer
from .services.gene_drug_service import search_gene_drugs_by_drug, search_gene_drugs_by_gene
from .services.gene_herb_service import (
    get_gene_herb_by_id,
    list_gene_herbs,
    search_gene_herbs_by_gene,
    search_gene_herbs_by_herb_name,
)
from .services.herb_ingredient_service import (
    get_herb_ingredient_by_name,
    search_herb_ingredients_by_gene,
    search_herb_ingredients_by_herb,
)
from .services.herb_lookup_service import resolve_herb_to_id
from .services.query_service import get_sentences_from_db, query_gene_knowledge


def _int_query(request, key: str, default: int) -> int:
    raw = request.GET.get(key)
    if raw is None or raw == "":
        return default
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return default


def _required_query(request, key: str):
    value = (request.GET.get(key) or "").strip()
    if not value:
        return None, JsonResponse({"error": f"query parameter '{key}' is required"}, status=400)
    return value, None

class GeneHerbViewSet(viewsets.ModelViewSet):
    queryset = GeneHerb.objects.all()
    serializer_class = GeneHerbSerializer
    # 允许在网页上通过 ?search=... 进行模糊搜索
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'gene', 'herb_id']
    ordering_fields = ['p_value', 'fdr_bh']

class HerbIngredientViewSet(viewsets.ModelViewSet):
    queryset = HerbIngredient.objects.all()
    serializer_class = HerbIngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['herb', 'ingredient_name','ingredient_id']


@require_GET
def health_check(_request):
    return JsonResponse({"status": "ok"})


@require_GET
def list_gene_herbs_api(request):
    limit = _int_query(request, "limit", 10)
    return JsonResponse(list_gene_herbs(limit), safe=False)


@require_GET
def get_gene_herb_api(request):
    record_id = request.GET.get("record_id") or request.GET.get("id")
    if not record_id:
        return JsonResponse({"error": "query parameter 'record_id' (or 'id') is required"}, status=400)
    try:
        data = get_gene_herb_by_id(int(record_id))
    except ValueError:
        return JsonResponse({"error": "record_id must be an integer"}, status=400)
    status = 404 if isinstance(data, dict) and data.get("error") else 200
    return JsonResponse(data, status=status)


@require_GET
def search_gene_herbs_by_gene_api(request):
    gene, err = _required_query(request, "gene")
    if err:
        return err
    limit = _int_query(request, "limit", 20)
    return JsonResponse(search_gene_herbs_by_gene(gene, limit), safe=False)


@require_GET
def search_gene_herbs_by_herb_name_api(request):
    name, err = _required_query(request, "name")
    if err:
        return err
    limit = _int_query(request, "limit", 20)
    return JsonResponse(search_gene_herbs_by_herb_name(name, limit), safe=False)


@require_GET
def search_gene_drugs_by_gene_api(request):
    gene, err = _required_query(request, "gene")
    if err:
        return err
    limit = _int_query(request, "limit", 20)
    return JsonResponse(search_gene_drugs_by_gene(gene, limit), safe=False)


@require_GET
def search_gene_drugs_by_drug_api(request):
    drug, err = _required_query(request, "drug")
    if err:
        return err
    limit = _int_query(request, "limit", 20)
    return JsonResponse(search_gene_drugs_by_drug(drug, limit), safe=False)


@require_GET
def search_herb_ingredients_by_herb_api(request):
    herb, err = _required_query(request, "herb")
    if err:
        return err
    limit = _int_query(request, "limit", 20)
    return JsonResponse(search_herb_ingredients_by_herb(herb, limit), safe=False)


@require_GET
def search_herb_ingredients_by_gene_api(request):
    gene, err = _required_query(request, "gene")
    if err:
        return err
    limit = _int_query(request, "limit", 20)
    return JsonResponse(search_herb_ingredients_by_gene(gene, limit), safe=False)


@require_GET
def get_herb_ingredient_by_name_api(request):
    ingredient_name, err = _required_query(request, "ingredient_name")
    if err:
        return err
    data = get_herb_ingredient_by_name(ingredient_name)
    status = 404 if isinstance(data, dict) and data.get("error") else 200
    return JsonResponse(data, status=status)


@require_GET
def query_gene_knowledge_api(request):
    gene, err = _required_query(request, "gene")
    if err:
        return err
    limit = _int_query(request, "limit", 10)
    return JsonResponse(query_gene_knowledge(gene, limit))


@require_GET
def get_gene_evidence_sentences_api(request):
    gene, err = _required_query(request, "gene")
    if err:
        return err
    limit = _int_query(request, "limit", 5)
    clean_gene = gene.strip().upper()
    evidence = get_sentences_from_db(clean_gene, limit)
    if not evidence:
        return JsonResponse({"message": f"未在数据库中找到关于 {clean_gene} 的证据句子。"})
    return JsonResponse({"gene": clean_gene, "evidence_list": evidence})


@require_GET
def resolve_herb_api(request):
    name, err = _required_query(request, "name")
    if err:
        return err
    result = resolve_herb_to_id(name)
    if result:
        return JsonResponse(result)
    return JsonResponse({"error": f"未找到与 {name} 对应的 herb_id"}, status=404)