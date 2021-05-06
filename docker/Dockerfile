FROM python:3.8-slim

# Install Auxiliary Software
RUN apt-get update
RUN apt-get install -y \
    make \
    apt-utils \
    apt-transport-https \
    curl \
    gcc \
    gnupg \
    gnupg-agent \
    graphviz \
    software-properties-common \
    vim

WORKDIR /src
COPY requirements.dev \
    requirements.prod \
    docker/Makefile \
    README.md \
    setup.py \
    mypy.ini \
    pylintrc \
    ./
RUN pip install -U pip
RUN pip install --requirement requirements.dev
RUN pip install --requirement requirements.prod
RUN pip install -e . 