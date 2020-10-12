FROM python:3.8

ENV DASH_DEBUG_MODE True

RUN pip install --upgrade pip

WORKDIR /pimms_dash

COPY requirements.txt .

RUN set -ex && \
    pip install -r requirements.txt

EXPOSE 8050

COPY pimms_dash .

CMD ["python", "index.py"]
