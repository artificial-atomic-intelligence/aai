FROM continuumio/miniconda3

WORKDIR /app
COPY . .
COPY aai.segment.yml .

# not sure why we need these lines but errors otherwise
# https://github.com/docker/buildx/issues/426
RUN export DOCKER_BUILDKIT=0
RUN export COMPOSE_DOCKER_CLI_BUILD=0

RUN conda env create -f aai.segment.yml

SHELL ["conda", "run", "-n", "aai_segment", "/bin/bash", "-c"]
RUN pip install .