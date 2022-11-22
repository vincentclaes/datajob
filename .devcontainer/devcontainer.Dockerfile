#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

# Update the VARIANT arg in devcontainer.json to pick a Python version: 3, 3.8, 3.7, 3.6
ARG VARIANT=3.8
FROM python:${VARIANT}

# If you would prefer to have multiple Python versions in your container,
# replace the FROM statement above with the following:
#
# FROM ubuntu:bionic
# ARG PYTHON_PACKAGES="python3.5 python3.6 python3.7 python3.8 python3 python3-pip python3-venv"
# RUN apt-get update && apt-get install --no-install-recommends -yq software-properties-common \
#     && add-apt-repository ppa:deadsnakes/ppa && apt-get update \
#     && apt-get install -yq --no-install-recommends ${PYTHON_PACKAGES} \
#     && pip3 install --no-cache-dir --upgrade pip setuptools wheel

# This Dockerfile adds a non-root user with sudo access. Use the "remoteUser"
# property in devcontainer.json to use it. On Linux, the container user's GID/UIDs
# will be updated to match your local UID/GID (when using the dockerFile property).
# See https://aka.ms/vscode-remote/containers/non-root-user for details.
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Uncomment the following COPY line and the corresponding lines in the `RUN` command if you wish to
# include your requirements in the image itself. Only do this if your requirements rarely change.
# COPY requirements.txt /tmp/pip-tmp/

# Default set of utilities to install in a side virtual env
ARG DEFAULT_UTILS="\
  pylint \
  flake8 \
  autopep8 \
  black \
  pytest \
  yapf \
  mypy \
  pydocstyle \
  pycodestyle \
  bandit \
  virtualenv \
  pipenv \
  poetry"

ENV PIPX_HOME=/usr/local/py-utils
ENV PIPX_BIN_DIR=${PIPX_HOME}/bin
ENV PATH=${PATH}:${PIPX_BIN_DIR}

# Options for common package install script
ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="true"
ARG COMMON_SCRIPT_SOURCE="https://raw.githubusercontent.com/microsoft/vscode-dev-containers/master/script-library/common-debian.sh"
ARG COMMON_SCRIPT_SHA="dev-mode"

# Configure apt and install packages
RUN apt-get update \
  && export DEBIAN_FRONTEND=noninteractive \
  #
  # Verify git, common tools / libs installed, add/modify non-root user, optionally install zsh
  && apt-get -y install --no-install-recommends curl ca-certificates 2>&1 \
  && curl -sSL  ${COMMON_SCRIPT_SOURCE} -o /tmp/common-setup.sh \
  && ([ "${COMMON_SCRIPT_SHA}" = "dev-mode" ] || (echo "${COMMON_SCRIPT_SHA} */tmp/common-setup.sh" | sha256sum -c -)) \
  && /bin/bash /tmp/common-setup.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" \
  && rm /tmp/common-setup.sh \
  #
  # Setup default python tools in a venv via pipx to avoid conflicts
  && mkdir -p ${PIPX_BIN_DIR} \
  && export PYTHONUSERBASE=/tmp/pip-tmp \
  && pip3 install --disable-pip-version-check --no-warn-script-location --no-cache-dir --user pipx \
  && /tmp/pip-tmp/bin/pipx install --pip-args=--no-cache-dir pipx \
  && echo "${DEFAULT_UTILS}" | xargs -n 1 /tmp/pip-tmp/bin/pipx install --system-site-packages --pip-args=--no-cache-dir \
  && chown -R ${USER_UID}:${USER_GID} ${PIPX_HOME} \
  && rm -rf /tmp/pip-tmp \
  #
  # Tactically remove imagemagick due to https://security-tracker.debian.org/tracker/CVE-2019-10131
  # Can leave in Dockerfile once upstream base image moves to > 7.0.7-28.
  && apt-get purge -y imagemagick imagemagick-6-common \
  #
  # Clean up
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/*

# Install github cli
RUN apt-get update && apt-get -y install software-properties-common \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0 \
  && apt-add-repository https://cli.github.com/packages \
  && apt-get update \
  && apt-get -y install gh

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
  && unzip awscliv2.zip \
  && ./aws/install \
  && rm awscliv2.zip

# install AWS CDK
# this worked to install a specific node version
# https://stackoverflow.com/a/62838796/1771155
ENV NVM_DIR /usr/local/nvm
RUN mkdir -p /usr/local/nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
ENV NODE_VERSION v14.13.1
RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION && nvm use --delete-prefix $NODE_VERSION"

ENV NODE_PATH $NVM_DIR/versions/node/$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/$NODE_VERSION/bin:$PATH
ENV AWS_DEFAULT_REGION=eu-west-1
RUN npm install -g aws-cdk@1.109.0
