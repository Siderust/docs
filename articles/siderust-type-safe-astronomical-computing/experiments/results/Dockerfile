# A clean scientific replay environment; no author workspace or caches are mounted.
FROM rust:1.93.1-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates \
    && python3 -m pip install --break-system-packages --no-cache-dir uv==0.12.0 \
    && rm -rf /var/lib/apt/lists/*
ENV CARGO_HOME=/scratch/cargo \
    UV_CACHE_DIR=/scratch/uv \
    UV_PYTHON_INSTALL_DIR=/scratch/python \
    UV_PYTHON_DOWNLOADS=automatic
WORKDIR /paper
