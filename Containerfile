FROM ghcr.io/clamsproject/clams-python:0.6.0

ARG CLAMS_APP_VERSION
ENV CLAMS_APP_VERSION ${CLAMS_APP_VERSION}

COPY ./ /app
WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["python3", "app.py", "--production"]
