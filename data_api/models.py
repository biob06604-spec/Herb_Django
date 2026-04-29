from django.db import models


class GeneHerb(models.Model):
    id = models.IntegerField(primary_key=True)
    herb_id = models.CharField(max_length=50, db_column='herb id', verbose_name="中药ID")
    full_name = models.CharField(max_length=255, db_column='full_name', verbose_name="完整药材名称")
    gene = models.CharField(max_length=50, db_column='gene', verbose_name="关联基因")
    pubmed_id = models.FloatField(db_column='PubMed ID', null=True, blank=True)
    reference_title = models.TextField(db_column='Reference title', null=True, blank=True)
    grade = models.CharField(max_length=10, db_column='Grade', null=True, blank=True)
    supporting_sentences = models.TextField(db_column='Supporting sentences', null=True, blank=True)
    relationship = models.CharField(max_length=100, db_column='Relationship', null=True, blank=True)
    p_value = models.FloatField(db_column='P value', null=True, blank=True)
    fdr_bh = models.FloatField(db_column='FDR BH', null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.gene}"

    class Meta:
        db_table = 'gene_herbs'
        managed = False


class GeneDrug(models.Model):
    id = models.IntegerField(primary_key=True, db_column='rowid')
    gene = models.CharField(max_length=100)
    drug = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'gene_drugs'


class HerbIngredient(models.Model):
    gene = models.CharField(max_length=100, db_column='Gene')
    herb = models.CharField(max_length=100, db_column='Herb')
    ingredient_id = models.CharField(max_length=100, db_column='Ingredient id')
    ingredient_name = models.CharField(max_length=200, db_column='Ingredient name', primary_key=True)
    ingredient_alias_name = models.CharField(max_length=200, db_column='Ingredient alias name')
    molecular_formula = models.CharField(max_length=100, db_column='Molecular formula')

    class Meta:
        managed = False
        db_table = 'herb_ingredients'

# data_api/models.py

class GeneSentence(models.Model):
    gene = models.CharField(max_length=100, db_column='Gene')
    sentence = models.TextField(db_column='Sentence')
    sentence_id = models.IntegerField(primary_key=True, db_column='Sentence_ID')

    class Meta:
        managed = False
        db_table = 'gene_sentences' 