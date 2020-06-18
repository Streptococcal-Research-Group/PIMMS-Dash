FROM python:3.7

ENV DASH_DEBUG_MODE True

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN set -ex && \
    pip install -r requirements.txt

EXPOSE 8050

COPY ./app .

CMD ["python", "dash_app.py"]
