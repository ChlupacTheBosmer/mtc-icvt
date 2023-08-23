# Use the official Miniconda3 image as the base image
FROM continuumio/miniconda3:latest
#continuumio/miniconda3:latest

# Update conda, install mamba, add a channel
RUN conda update conda

RUN conda install -c conda-forge mamba
RUN apt-get update && apt-get install -y libarchive-dev

# Set the working directory
WORKDIR /ICVT

#RUN mamba update -n base -c defaults conda

## Install GIT
#RUN conda install git
# Install libarchive library

# Clone the repository
RUN git clone https://github.com/ChlupacTheBosmer/ICVT

# Install required packages and dependencies
RUN pip install opencv-contrib-python>=4.8.0.74
RUN mamba install --verbose -c conda-forge Pillow>=9.5.0
RUN mamba install --verbose -c conda-forge pandas>=2.0.0
RUN mamba install --verbose -c conda-forge xlwings>=0.30.5
#RUN mamba install --verbose -c conda-forge hachoir-parser
#RUN mamba install --verbose -c conda-forge hachoir-metadata
RUN mamba install --verbose -c conda-forge imageio
RUN mamba install --verbose -c conda-forge google-cloud-vision
RUN mamba install --verbose -c conda-forge openpyxl
RUN mamba install --verbose -c conda-forge typing_extensions>=4.5.0
# numpy>=1.24.2

# Cleanup
# RUN conda clean -afy

## Run the installation
#RUN python construct_singularity.py

# Define the command to run when the container is executed
#CMD ["python", "construct_singularity.py"]