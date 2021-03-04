FROM continuumio/miniconda3

WORKDIR /app
COPY . .
COPY aai.io.yml .

# not sure why we need these lines but errors otherwise
# https://github.com/docker/buildx/issues/426
RUN export DOCKER_BUILDKIT=0
RUN export COMPOSE_DOCKER_CLI_BUILD=0

RUN conda env create -f aai.io.yml

SHELL ["conda", "run", "-n", "aai_io", "/bin/bash", "-c"]
RUN pip install .