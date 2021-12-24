FROM gcr.io/spark-operator/spark-py:v3.0.0
MAINTAINER Lucas M.E. Ferreira <lucas.m.e.ferreira@gmail.com>

USER root:root

RUN mkdir -p /app

COPY spark_stock_analytics.py /app/

COPY ./jars/ /opt/spark/jars

WORKDIR /app

USER 1001
