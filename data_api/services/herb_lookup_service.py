from data_api.models import GeneHerb


def resolve_herb_to_id(query: str) -> dict | None:
    """
    根据 herb_id、中文名、英文名、别名解析出标准 herb_id
    数据来源：gene_herbs 表中的 herb_id + full_name
    """
    q = query.strip()
    if not q:
        return None

    # 1. 用户直接输入 HERB 编号
    if q.upper().startswith("HERB"):
        record = (
            GeneHerb.objects
            .filter(herb_id__iexact=q)
            .values("herb_id", "full_name")
            .first()
        )
        if record:
            return {
                "herb_id": record["herb_id"],
                "full_name": record["full_name"],
                "matched_by": "herb_id",
            }

    # 2. 在 full_name 中模糊匹配中文/英文/别名
    record = (
        GeneHerb.objects
        .filter(full_name__icontains=q)
        .values("herb_id", "full_name")
        .first()
    )
    if record:
        return {
            "herb_id": record["herb_id"],
            "full_name": record["full_name"],
            "matched_by": "full_name",
        }

    return None