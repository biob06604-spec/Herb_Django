from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"herbs", views.GeneHerbViewSet)
router.register(r"ingredients", views.HerbIngredientViewSet)

urlpatterns = [
    path("health", views.health_check, name="data_api_health"),
    path("query/list_gene_herbs", views.list_gene_herbs_api, name="list_gene_herbs_api"),
    path("query/get_gene_herb", views.get_gene_herb_api, name="get_gene_herb_api"),
    path(
        "query/search_gene_herbs_by_gene",
        views.search_gene_herbs_by_gene_api,
        name="search_gene_herbs_by_gene_api",
    ),
    path(
        "query/search_gene_herbs_by_herb_name",
        views.search_gene_herbs_by_herb_name_api,
        name="search_gene_herbs_by_herb_name_api",
    ),
    path(
        "query/search_gene_drugs_by_gene",
        views.search_gene_drugs_by_gene_api,
        name="search_gene_drugs_by_gene_api",
    ),
    path(
        "query/search_gene_drugs_by_drug",
        views.search_gene_drugs_by_drug_api,
        name="search_gene_drugs_by_drug_api",
    ),
    path(
        "query/search_herb_ingredients_by_herb",
        views.search_herb_ingredients_by_herb_api,
        name="search_herb_ingredients_by_herb_api",
    ),
    path(
        "query/search_herb_ingredients_by_gene",
        views.search_herb_ingredients_by_gene_api,
        name="search_herb_ingredients_by_gene_api",
    ),
    path(
        "query/get_herb_ingredient_by_name",
        views.get_herb_ingredient_by_name_api,
        name="get_herb_ingredient_by_name_api",
    ),
    path(
        "query/query_gene_knowledge",
        views.query_gene_knowledge_api,
        name="query_gene_knowledge_api",
    ),
    path(
        "query/get_gene_evidence_sentences",
        views.get_gene_evidence_sentences_api,
        name="get_gene_evidence_sentences_api",
    ),
    path("query/resolve_herb", views.resolve_herb_api, name="resolve_herb_api"),
]

urlpatterns += router.urls
