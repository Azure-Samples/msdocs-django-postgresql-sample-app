ARG VARIANT=3
FROM --platform=amd64 mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

RUN curl -fsSL https://aka.ms/install-azd.sh | bash

ENV PYTHONUNBUFFERED 1

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client
