# Mars Greenhouse Ops — hero-tools MCP server image.
# Build context MUST be the demo root (demos/mars-greenhouse-ops) so the image can bundle the shared
# mock-backends the server reuses:
#   az acr build -r <registry> -f cloud/mcp-server/Dockerfile -t marsgreenhouse-mcp:latest .
FROM python:3.12-slim

WORKDIR /app

COPY cloud/mcp-server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY cloud/mcp-server/server.py ./
COPY mock-backends/tools.json ./mock-backends/tools.json
COPY mock-backends/hero_tools ./mock-backends/hero_tools

ENV PORT=8000 \
    MARS_MOCK_BACKENDS=/app/mock-backends

EXPOSE 8000
CMD ["python", "server.py"]
