from data_api.services.gene_herb_service import search_gene_herbs_by_gene
from data_api.services.gene_drug_service import search_gene_drugs_by_gene
from data_api.services.herb_ingredient_service import search_herb_ingredients_by_gene
from data_api.models import GeneSentence


def query_gene_knowledge(gene: str, limit: int = 10) -> dict:
    herbs = search_gene_herbs_by_gene(gene, limit)
    drugs = search_gene_drugs_by_gene(gene, limit)
    ingredients = search_herb_ingredients_by_gene(gene, limit)

    return {
        "gene": gene,
        "herbs": herbs,
        "drugs": drugs,
        "ingredients": ingredients
    }

def get_sentences_from_db(gene_symbol, limit=5):
    """仅提取数据库中实际存在的字段"""
    records = GeneSentence.objects.filter(
        gene__iexact=gene_symbol
    ).values('sentence', 'sentence_id')[:limit] # 删除了 pmid 和 reference_title
    
    return list(records)