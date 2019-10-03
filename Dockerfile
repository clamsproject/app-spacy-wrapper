FROM python:3.7


COPY ./ ./app
WORKDIR ./app
RUN pip install -r requirements.txt

# install git
RUN apt-get update && \
    apt-get install -y git

ENTRYPOINT ["python"]
CMD ["app.py"]