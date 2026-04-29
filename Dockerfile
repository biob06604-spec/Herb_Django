FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# MCP HTTP 监听端口
EXPOSE 8087

ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8087

# 启动 MCP 服务
CMD ["python", "mcp_server.py"]
