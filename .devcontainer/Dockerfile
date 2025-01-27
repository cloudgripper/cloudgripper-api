FROM condaforge/miniforge3:24.3.0-0

# RUN sudo apt-get update && sudo apt-get install -y \
#     libx11-xcb1 \
#     libxrender1 \
#     libxcb-render0 \
#     libxcb-shm0 \
#     libxcb1 \
#     libxext6 \
#     libsm6 \
#     libglib2.0-0

ARG HOME=/root
ARG CTAGS_DIR=$HOME/tools/ctags
ARG RIPGREP_DIR=$HOME/tools/ripgrep
ARG ANACONDA_DIR=$HOME/tools/anaconda
ARG NVIM_CONFIG_DIR=$HOME/.config/nvim

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# Install common dev tools
RUN apt-get update --allow-unauthenticated \
    && apt-get install --allow-unauthenticated -y git curl autoconf pkg-config zsh locales neovim

# python packages
RUN pip install pynvim jedi pylint flake8

# Install ripgrep
RUN curl -Lo /tmp/ripgrep.tar.gz https://github.com/BurntSushi/ripgrep/releases/download/11.0.0/ripgrep-11.0.0-x86_64-unknown-linux-musl.tar.gz \
    && cd /tmp \
    && mkdir -p ${RIPGREP_DIR} \
    && tar zxf ripgrep.tar.gz -C ${RIPGREP_DIR} --strip-components=1 \
    && rm -rf /tmp/ripgrep.tar.gz
ENV PATH=${RIPGREP_DIR}:$PATH

