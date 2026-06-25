FROM pandoc/minimal:latest-static AS init
FROM python:3.12.2-alpine3.18 AS build

ENV BUILD_DEPS="\
    build-base \
    bzip2-dev \
    zlib-dev \
    xz-dev \
    openssl-dev \
    curl-dev \
    gfortran \
    openblas-dev \
    linux-headers \
    libffi-dev \
    cmake \
    pkgconf \
    gcc \
    musl-dev \
    git"

WORKDIR /data
COPY requirements.txt ./
COPY sphinx.txt ./

RUN apk upgrade --update && \
    apk add --no-cache --virtual .build-deps $BUILD_DEPS && \
    pip install --upgrade pip && \
    pip install --upgrade pip setuptools && \
    # installing outside of requirements to install statsmodels
    pip install "setuptools_scm[toml]" && \
    pip install "pandas>=1.3" && \
    pip install "numpy>=1.26" && \
    pip install "scipy >= 1.5" && \
    # this leaves cython unoptimised (fine, only need it for statsmodels)
    pip install "cython >= 0.29.33" --no-binary :all: && \
    # installing statsmodel from 
    # https://pypi.org/project/statsmodels/#files
    # the no-build-isolation flag ensures statsmodels has to use the previously installed packages
    pip install "statsmodels==0.14.1" --no-build-isolation &&\
    pip install -r requirements.txt && \
    pip install -r sphinx.txt && \
    apk del .build-deps

FROM python:3.12.2-alpine3.18 AS final
ENV PERSISTENT_DEPS="\
    make \
    openblas \
    curl \
    git \
    sed"

WORKDIR /data
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/share/jupyter /usr/local/share/jupyter
# COPY --from=init /pandoc /usr/local/bin/
COPY --from=init /usr/local/bin/pandoc /usr/local/bin/

RUN apk add --no-cache --virtual .persistent-deps $PERSISTENT_DEPS
