FROM ubuntu:24.04

# Install Python 3.14 from deadsnakes PPA (if available)
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.14 python3.14-venv && \
	#python3.14-distutils &&  \
    apt-get clean

# Optional: set python3 to python3.14
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1

