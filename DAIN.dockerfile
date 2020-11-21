FROM nvidia/cuda:11.1-cudnn8-devel-ubuntu18.04

LABEL maintainer="samuel.mauck@colorado.edu"

RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-compat-11-1 \
    curl \
    ffmpeg \
    python3 \
    python3-dev \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

RUN ["/bin/bash", "-c", "set -o pipefail && curl https://bootstrap.pypa.io/get-pip.py | python3"]

RUN pip3 install --no-cache-dir torch==1.4.0 numpy opencv-python Pillow

WORKDIR /usr/src/app

RUN ["/bin/bash", "-c", "set -o pipefail && mkdir VFIN && curl -L https://github.com/iBobbyTS/VFIN/tarball/bc1ca0fa56a5297ebac1ab9e33e99e8bb0c72cfe | tar --strip 1 -xzC ./VFIN"]

WORKDIR /usr/src/app/VFIN/DAIN

RUN python3 build.py -cc 61

ADD http://vllab1.ucmerced.edu/~wenbobao/DAIN/best.pth ./model_weights/
