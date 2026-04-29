import os
import django

# ========================
# Django 初始化
# ========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "herbapi.settings")
django.setup()

from asgiref.sync import sync_to_async
from mcp.server.fastmcp import FastMCP

# ========================
# Service 导入
# ========================
from data_api.services.gene_herb_service import (
    list_gene_herbs,
    get_gene_herb_by_id,
    search_gene_herbs_by_gene,
    search_gene_herbs_by_herb_name,
)

from data_api.services.gene_drug_service import (
    search_gene_drugs_by_gene,
    search_gene_drugs_by_drug,
)

from data_api.services.herb_ingredient_service import (
    search_herb_ingredients_by_herb,
    search_herb_ingredients_by_gene,
    get_herb_ingredient_by_name,
)

from data_api.services.query_service import query_gene_knowledge
from data_api.services.herb_lookup_service import resolve_herb_to_id
from data_api.services.query_service import get_sentences_from_db

# ========================
# MCP 实例
# ========================
mcp = FastMCP("herbapi")


# ========================
# 工具函数（增加异常保护）
# ========================
async def safe_call(func, *args, **kwargs):
    try:
        return await sync_to_async(func)(*args, **kwargs)
    except Exception as e:
        return {"error": str(e)}


# ========================
# 工具定义
# ========================
@mcp.tool()
def get_gene_evidence_sentences(gene: str, limit: int = 5):
    """
    根据基因名称获取科研证据句子及其编号。
    """

    # 清洗输入
    clean_gene = gene.strip().upper()
    sentences_data = get_sentences_from_db(clean_gene, limit)

    if not sentences_data:
        return {"message": f"未在数据库中找到关于 {gene} 的证据句子。"}

    return {
        "gene": clean_gene,
        "evidence_list": sentences_data  # 此时 list 中只含 sentence 和 sentence_id
    }

@mcp.tool()
def resolve_herb_tool(name: str) -> dict:
    """根据中药名称、别名或 herb_id 解析标准 herb_id"""
    try:
        result = resolve_herb_to_id(name)
        if result:
            return result
        return {"error": f"未找到与 {name} 对应的 herb_id"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def list_gene_herbs_tool(limit: int = 10):
    return await safe_call(list_gene_herbs, limit=limit)


@mcp.tool()
async def get_gene_herb_tool(record_id: int):
    return await safe_call(get_gene_herb_by_id, record_id)


@mcp.tool()
async def search_gene_herbs_by_gene_tool(gene: str, limit: int = 20):
    return await safe_call(search_gene_herbs_by_gene, gene=gene, limit=limit)


@mcp.tool()
async def search_gene_herbs_by_herb_name_tool(name: str, limit: int = 20):
    return await safe_call(search_gene_herbs_by_herb_name, name=name, limit=limit)


@mcp.tool()
async def search_gene_drugs_by_gene_tool(gene: str, limit: int = 20):
    return await safe_call(search_gene_drugs_by_gene, gene=gene, limit=limit)


@mcp.tool()
async def search_gene_drugs_by_drug_tool(drug: str, limit: int = 20):
    return await safe_call(search_gene_drugs_by_drug, drug=drug, limit=limit)


@mcp.tool()
async def search_herb_ingredients_by_herb_tool(herb: str, limit: int = 20):
    return await safe_call(search_herb_ingredients_by_herb, herb=herb, limit=limit)


@mcp.tool()
async def search_herb_ingredients_by_gene_tool(gene: str, limit: int = 20):
    return await safe_call(search_herb_ingredients_by_gene, gene=gene, limit=limit)


@mcp.tool()
async def get_herb_ingredient_by_name_tool(ingredient_name: str):
    return await safe_call(get_herb_ingredient_by_name, ingredient_name)


@mcp.tool()
async def query_gene_knowledge_tool(gene: str, limit: int = 10):
    return await safe_call(query_gene_knowledge, gene=gene, limit=limit)


# ========================
# Resource
# ========================
@mcp.resource("geneherb://{record_id}")
async def gene_herb_resource(record_id: str):
    return await safe_call(get_gene_herb_by_id, int(record_id))


# ========================
# 启动
# ========================
if __name__ == "__main__":
    import uvicorn
    import logging
    import sys
    from contextlib import asynccontextmanager
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route, Mount
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    from starlette.middleware.cors import CORSMiddleware

    # 配置详细日志
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger("mcp_server")

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8087"))
    
    logger.info(f"!!! 正在启动 MCP 服务 (文件位置: {__file__}) !!!")

    # 优先使用 streamable-http 入口，避免 SSE 的 Request validation 限制。
    if hasattr(mcp, "streamable_http_app"):
        mcp_http_app = mcp.streamable_http_app()
    else:
        raise RuntimeError("当前 mcp 版本不支持 streamable_http_app，无法通过 /mcp 提供服务")

    async def mcp_proxy_app(scope, receive, send):
        # Forward the request as-is. Some MCP versions reject a rewritten Host header
        # with 421 (Misdirected Request), so we avoid mutating headers here.
        await mcp_http_app(scope, receive, send)

    async def ping(request):
        return JSONResponse({"status": "ok", "message": "Pong!"})

    # 手动定义所有路由
    routes = [
        Route("/ping", endpoint=ping),
        # Mount at root so FastMCP streamable-http app can serve its own /mcp path.
        Mount("/", app=mcp_proxy_app),
    ]

    @asynccontextmanager
    async def lifespan(_app):
        # streamable_http_app 作为子应用被 Mount 时，其 lifespan 不会自动执行。
        # 这里显式进入子应用 lifespan，确保 session manager 的 task group 初始化。
        subapp_lifespan = None
        if hasattr(mcp_http_app, "router") and hasattr(mcp_http_app.router, "lifespan_context"):
            subapp_lifespan = mcp_http_app.router.lifespan_context(mcp_http_app)
            await subapp_lifespan.__aenter__()
        elif hasattr(mcp_http_app, "router") and hasattr(mcp_http_app.router, "startup"):
            # 兼容兜底
            await mcp_http_app.router.startup()
        try:
            yield
        finally:
            if subapp_lifespan is not None:
                await subapp_lifespan.__aexit__(None, None, None)
            elif hasattr(mcp_http_app, "router") and hasattr(mcp_http_app.router, "shutdown"):
                await mcp_http_app.router.shutdown()

    app = Starlette(routes=routes, lifespan=lifespan)

    # 在最外层加一个最宽松的中间件
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    logger.info("采用 streamable-http 模式，MCP 入口: /mcp")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        http="h11",
        log_level="info",
    )
