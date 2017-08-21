FROM alpine:latest

ENV APP_SRC=/opt/source \
    VICTIMS_BASE_DIR=/var/run/victims

RUN apk --update --no-cache add \
        python python-dev py2-pip py-cffi \
        g++ \
    && install -d ${VICTIMS_BASE_DIR} ${APP_SRC}

WORKDIR ${APP_SRC}
ENV PYTHONPATH=${APP_SRC}

RUN adduser -S victims &&
	usermod -a -G root victims
USER victims

ADD . .

CMD ["python", "-m", "victims.web"]
