FROM condaforge/mambaforge:4.9.2-5 as conda

RUN mkdir /app
WORKDIR /app
COPY . .
COPY conda-linux-64.lock .

## not sure why we need these lines but errors otherwise
## https://github.com/docker/buildx/issues/426
RUN export DOCKER_BUILDKIT=0
RUN export COMPOSE_DOCKER_CLI_BUILD=0

# Make env from lockfile and delete tarballs
RUN mamba create --name aai_cpu --file conda-linux-64.lock && \ 
    conda clean -afy

## install pip dependences and aai api
RUN conda run -n aai_cpu python -m pip install -r requirements.cpu.txt
RUN conda run -n aai_cpu python -m pip install .

SHELL ["conda", "run", "-n", "aai_cpu", "/bin/bash", "-c"]

COPY main.py .
EXPOSE 8000

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "aai_cpu", "python", "main.py"]