from chat.services.llm_service import decide_tool, summarize_with_tool_result
from chat.services.mcp_client import call_mcp_tool


TOOL_NAME_MAP = {
    "query_gene_knowledge": "query_gene_knowledge_tool",
    "search_gene_herbs_by_gene": "search_gene_herbs_by_gene_tool",
    "search_gene_drugs_by_gene": "search_gene_drugs_by_gene_tool",
    "search_herb_ingredients_by_herb": "search_herb_ingredients_by_herb_tool",
    "get_gene_evidence_sentences": "get_gene_evidence_sentences",
}

# 参数清洗
def normalize_arguments(tool_name: str, arguments: dict) -> dict:
    arguments = arguments or {}

    if tool_name in {"query_gene_knowledge", "search_gene_herbs_by_gene", "search_gene_drugs_by_gene"}:
        gene = arguments.get("gene", "")
        return {
            "gene": gene.strip().upper(),
            "limit": 10,
        }

    if tool_name == "get_gene_evidence_sentences":
        gene = arguments.get("gene", "")
        return {
            "gene": gene.strip().upper(),
            "limit": 5,
        }

    if tool_name == "search_herb_ingredients_by_herb":
        herb = arguments.get("herb", "")
        return {
            "herb": herb.strip(),
            "limit": 10,
        }

    return arguments


def handle_user_message(message: str) -> dict:
    # 调用 LLM 决定工具
    decision = decide_tool(message)

    tool_name = decision.get("tool_name")
    arguments = decision.get("arguments", {})

    if not tool_name:
        return {
            "answer": "我暂时无法判断该调用哪个查询工具，请换一种更明确的提问方式。",
            "tool_used": None,
            "tool_result": None,
        }

    mcp_tool_name = TOOL_NAME_MAP.get(tool_name)
    if not mcp_tool_name:
        return {
            "answer": f"暂不支持工具：{tool_name}",
            "tool_used": tool_name,
            "tool_result": None,
        }


    normalized_args = normalize_arguments(tool_name, arguments)
    # 调用 MCP Client 获取真实数据
    tool_result = call_mcp_tool(mcp_tool_name, normalized_args)

    answer = summarize_with_tool_result(
        user_message=message,
        tool_name=tool_name,
        tool_result=tool_result,
    )

    return {
        "answer": answer,
        "tool_used": mcp_tool_name,
        "tool_result": tool_result,
    }