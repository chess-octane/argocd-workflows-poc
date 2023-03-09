#-- Builder image
FROM python:3.10-slim AS builder
ARG NPM_CONFIG_REGISTRY
ARG NPM_CONFIG__AUTH
ARG PIP_INDEX_URL
ENV NPM_CONFIG_ALWAYS_AUTH=true
WORKDIR /build
COPY requirements.txt /build/

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt

#-- Deployment image
FROM python:3.10-slim as deployment
WORKDIR /app
COPY main.py /app/
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["python", "main.py"]
