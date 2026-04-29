from data_api.models import GeneDrug


def serialize_gene_drug(obj: GeneDrug) -> dict:
    return {
        "gene": obj.gene,
        "drug": obj.drug,
    }


def search_gene_drugs_by_gene(gene: str, limit: int = 20) -> list[dict]:
    queryset = GeneDrug.objects.filter(gene__icontains=gene)[:limit]
    return [serialize_gene_drug(obj) for obj in queryset]


def search_gene_drugs_by_drug(drug: str, limit: int = 20) -> list[dict]:
    queryset = GeneDrug.objects.filter(drug__icontains=drug)[:limit]
    return [serialize_gene_drug(obj) for obj in queryset]