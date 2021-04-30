FROM python:3.6-slim-buster

# for debugging only, can be removed to save space
RUN apt-get update && apt-get -y install vim curl

WORKDIR ./app

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./ ./

CMD ["python3", "app.py"]
