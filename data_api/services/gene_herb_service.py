from data_api.models import GeneHerb
from django.core.exceptions import ObjectDoesNotExist


def serialize_gene_herb(obj: GeneHerb) -> dict:
    return {
        "id": obj.id,
        "herb_id": obj.herb_id,
        "full_name": obj.full_name,
        "gene": obj.gene,
        "pubmed_id": obj.pubmed_id,
        "reference_title": obj.reference_title,
        "grade": obj.grade,
        "supporting_sentences": obj.supporting_sentences,
        "relationship": obj.relationship,
        "p_value": obj.p_value,
        "fdr_bh": obj.fdr_bh,
    }


def list_gene_herbs(limit: int = 10) -> list[dict]:
    queryset = GeneHerb.objects.all()[:limit]
    return [serialize_gene_herb(obj) for obj in queryset]


def get_gene_herb_by_id(record_id: int) -> dict:
    try:
        obj = GeneHerb.objects.get(id=record_id)
        return serialize_gene_herb(obj)
    except ObjectDoesNotExist:
        return {"error": f"GeneHerb with id={record_id} not found"}


def search_gene_herbs_by_gene(gene: str, limit: int = 20) -> list[dict]:
    queryset = GeneHerb.objects.filter(gene__icontains=gene)[:limit]
    return [serialize_gene_herb(obj) for obj in queryset]


def search_gene_herbs_by_herb_name(name: str, limit: int = 20) -> list[dict]:
    queryset = GeneHerb.objects.filter(full_name__icontains=name)[:limit]
    return [serialize_gene_herb(obj) for obj in queryset]