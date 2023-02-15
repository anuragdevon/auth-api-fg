# -------------------------------------------------------
# Official Docker python image
FROM python:3.10-slim-buster as base

# Setup No buffer for python output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update python pip
RUN pip install --upgrade pip

# Setup working directory
RUN mkdir -p /src
WORKDIR /src

# Add Files
ADD src /src/
COPY requirements.txt /src/

# Install project dependencies
RUN pip install -r /src/requirements.txt
# RUN --mount=type=cache,target=/root/.cache/pip pip install -r /auth/requirements.txt

# Expose ports
EXPOSE 8080

# Start Sub-processes
WORKDIR /src
CMD export ENVIRONMENT=".env_prod" && python service.py | tee /service.log
# -------------------------------------------------------