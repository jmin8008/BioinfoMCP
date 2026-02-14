
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update &&     apt-get install -y         default-jre         wget         curl     && apt-get clean     && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh &&     bash /tmp/miniconda.sh -b -p /opt/conda &&     rm /tmp/miniconda.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Install qiime_tools_inspect_metadata via conda (e.g., from bioconda)
RUN conda install -c bioconda qiime_tools_inspect_metadata -y &&     conda clean -a

# Install Python dependencies
RUN pip install uv
RUN uv pip install --system fastmcp

# Create app directory
WORKDIR /app

# Copy your MCP server
COPY qiime_tools_inspect_metadata_server.py /app/

# Create workspace and output directories
RUN mkdir -p /app/workspace /app/output

# Make sure the server script is executable
RUN chmod +x /app/qiime_tools_inspect_metadata_server.py

# Expose port for MCP over HTTP (optional)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3     CMD python -c "import sys; sys.exit(0)"

# Default command runs the MCP server via stdio
CMD ["python", "/app/qiime_tools_inspect_metadata_server.py"]
        