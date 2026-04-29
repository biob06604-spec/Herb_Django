import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")


def get_llm_client():
    if not LLM_API_KEY:
        raise ValueError("未配置 LLM_API_KEY")
    if not LLM_BASE_URL:
        raise ValueError("未配置 LLM_BASE_URL")
    if not LLM_MODEL:
        raise ValueError("未配置 LLM_MODEL")

    return OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
    )


def decide_tool(user_message: str) -> dict:
    client = get_llm_client()

    # 确保开头是三个引号，末尾也是三个引号
    system_prompt = """
你是一个专业的中药-基因-药物知识助手。你的任务是根据用户问题，选择最合适的工具。

可用工具如下:

1. query_gene_knowledge
- 作用: 综合查询某个基因相关的中药、药物、成分以及关联的文献证据句子。
- 参数: gene (必须是大写的 Gene Symbol)

2. search_gene_herbs_by_gene
- 作用: 根据基因查询相关中药。
- 参数: gene

3. search_gene_drugs_by_gene
- 作用: 根据基因查询相关药物。
- 参数: gene

4. get_gene_evidence_sentences
- 作用: 从专门的科研文献数据库中调取与该基因直接相关的原始证据原话。
- 参数: gene (需为大写 Symbol，如 STAT3)
- 适用场景: 当用户询问“有什么证据？”、“原理是什么？”、“某基因如何影响疾病？”或需要展示原始论文描述时必用。

5. search_herb_ingredients_by_herb
- 作用: 根据中药名称查询成分。
- 参数: herb

请严格返回 JSON 格式，不要输出多余解释。

返回格式必须是以下之一:

情况1: 需要调用工具
{
  "tool_name": "query_gene_knowledge",
  "arguments": {
    "gene": "AHR"
  }
}

情况2: 不需要调用工具
{
  "tool_name": null,
  "arguments": {}
}
"""

    user_prompt = f"用户问题: {user_message}"

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    content = completion.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "tool_name": None,
            "arguments": {}
        }


def summarize_with_tool_result(user_message: str, tool_name: str, tool_result: dict) -> str:
    client = get_llm_client()

    system_prompt = """
你是一个科研助手。当工具返回 evidence_list 时，请按以下格式展示：

### 🔬 科研证据摘要
> "[这里填入数据库中的 Sentence 原文]" 
> —— *证据来源 ID: [这里填入 Sentence_ID]*

要求：
1. 如果有多个句子，请分点列出，每条不超过 3 条最相关的。
2. 如果句子是英文，请在下方提供简短的中文核心语义解释。
3. 保持客观中立，不要过度解读。
"""

    # ... 剩下的调用逻辑保持不变

    user_prompt = f"""
用户问题：
{user_message}

使用的工具：
{tool_name}

工具返回结果：
{tool_result}

请生成最终回答。
"""

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.3,
    )

    return completion.choices[0].message.content.strip()