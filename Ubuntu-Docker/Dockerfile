FROM ubuntu:22.04 AS rin_ubuntu_base
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install curl wget libffi-dev gcc-12 clang dos2unix git -y
RUN curl -O https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer