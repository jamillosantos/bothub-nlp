FROM ilha/scipy:python3.6-alpine3.7

ENV WORKDIR /home/app
ENV IS_PRODUCTION true
ENV PORT 2657

WORKDIR $WORKDIR

RUN apk update && apk upgrade && \
    apk add alpine-sdk postgresql-dev libpng openblas-dev freetype-dev libpng-dev

RUN pip install pipenv psycopg2-binary

COPY Pipfile .
COPY Pipfile.lock .
COPY Makefile .

RUN make check_environment

COPY . .

ARG DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD
RUN if [ ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD} ]; \
        then python scripts/download_spacy_models.py ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD}; \
    fi
ENV DOWNLOADED_LANGUAGES ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD}

RUN make import_ilha_spacy_langs CHECK_ENVIRONMENT=false

RUN chmod +x ./docker/bothub-nlp/entrypoint.sh
ENTRYPOINT $WORKDIR/docker/bothub-nlp/entrypoint.sh