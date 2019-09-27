FROM python:3.7


COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY ./ ./app
WORKDIR ./app

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

ENTRYPOINT ["python"]
CMD ["app.py"]