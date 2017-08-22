FROM alpine:latest

ENV APP_SRC=/opt/source \
    VICTIMS_BASE_DIR=/var/run/victims \
    PYTHONPATH=${APP_SRC}

RUN apk --update --no-cache add \
        python python-dev py2-pip py-cffi \
        g++ \
    && install -d ${VICTIMS_BASE_DIR} ${APP_SRC}

WORKDIR ${APP_SRC}

ADD . .

RUN pip install -r requirements.txt

RUN adduser -S -G root -u 1001 victims

RUN chown -R 1001:0 ${APP_SRC} && chmod -R ug+rwx ${APP_SRC} && \
    chown -R 1001:0 ${VICTIMS_BASE_DIR} && chmod -R ug+rwx ${VICTIMS_BASE_DIR}

USER victims

CMD ["python", "-m", "victims.web"]
