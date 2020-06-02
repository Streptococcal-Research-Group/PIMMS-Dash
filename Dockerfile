FROM python:3.7

ENV DASH_DEBUG_MODE True

RUN set -ex && \
    pip install dash && \
    pip install pandas

EXPOSE 8050

COPY ./app /app

WORKDIR /app

CMD ["python", "dash_app.py"]
