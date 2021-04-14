FROM clamsproject/clams-python:0.2.0

RUN mkdir ./app
WORKDIR ./app
# download dbpedia-spotlight and its English model
RUN wget -q https://sourceforge.net/projects/dbpedia-spotlight/files/spotlight/dbpedia-spotlight-1.0.0.jar
RUN wget -qO- http://downloads.dbpedia.org/repo/dbpedia/spotlight/spotlight-model/2020.11.18/spotlight-model_lang%3den.tar.gz | tar xzf -

#Install default Java 11
RUN apt-get update
RUN apt-get install -y default-jdk-headless

COPY ./ ./
RUN pip3 install -r requirements.txt
CMD java -jar dbpedia-spotlight-1.0.0.jar en http://localhost:2222/rest & python3 app.py ;
