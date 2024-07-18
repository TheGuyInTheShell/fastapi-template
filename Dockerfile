# Base image with Miniconda
FROM python:3.11-slim

# Install wget
RUN apt-get update && apt-get install -y wget dos2unix

RUN mkdir -p ~/miniconda3
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
RUN bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
RUN rm -rf ~/miniconda3/miniconda.sh

# Set environment name and working directorydokcer 
ENV CONDA_ENV_NAME current

WORKDIR /

ENV TZ=America/Caracas

RUN ln -sf /usr/share/zoneinfo/America/Caracas /etc/localtime && \
    echo "America/Caracas" > /etc/timezone

RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libpng16-16

# Create conda environment
RUN ~/miniconda3/bin/conda create -n $CONDA_ENV_NAME python=3.11

# Directly source the conda initialization script for bash
RUN echo "source ~/miniconda3/etc/profile.d/conda.sh" >> ~/.bashrc

# Activate conda environment
RUN echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc

# Install packages from requirements.txt
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy your application code
COPY . .

RUN python --version

# Convert line endings of uvicorn_start.sh to Unix style
RUN dos2unix start.sh

EXPOSE 8000

CMD ["bash", "./start.sh"]
