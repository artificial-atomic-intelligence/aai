FROM continuumio/anaconda3

RUN mkdir /app
WORKDIR /app
COPY . .
COPY aai.cpu.yml .

# not sure why we need these lines but errors otherwise
# https://github.com/docker/buildx/issues/426
RUN export DOCKER_BUILDKIT=0
RUN export COMPOSE_DOCKER_CLI_BUILD=0

RUN conda env create -f aai.cpu.yml

SHELL ["conda", "run", "-n", "aai_cpu", "/bin/bash", "-c"]
RUN pip install .

COPY main.py .
EXPOSE 8080

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "aai_cpu", "python", "main.py"]