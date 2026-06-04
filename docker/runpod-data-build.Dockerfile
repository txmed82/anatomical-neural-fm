FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && python -m pip install \
        boto3 \
        h5py \
        numpy \
        one-api \
        iblatlas \
        temporaldata

WORKDIR /workspace
CMD ["bash", "-lc", "python --version && sleep infinity"]
