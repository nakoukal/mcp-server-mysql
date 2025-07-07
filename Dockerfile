FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install build dependencies and package dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY mysql_server.py ./

# Install package in development mode
RUN pip install --no-cache-dir -e .

# Expose port 8000 (internally where FastMCP runs)
EXPOSE 8000

# Set environment variables with defaults that can be overridden at runtime
ENV PYTHONUNBUFFERED=1

# FastMCP will run on internal port 8000
ENV FASTMCP_HOST="0.0.0.0"
ENV FASTMCP_PORT="8000"
ENV FASTMCP_LOG_LEVEL="DEBUG"

# Run the FastMCP server with new Streamable HTTP transport (MCP 2024-11-05+)
ENTRYPOINT ["python", "mysql_server.py"]
CMD ["--transport", "streamable-http", "--port", "8000"]
