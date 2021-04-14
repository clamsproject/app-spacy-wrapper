FROM clamsproject/clams-python:0.2.0

COPY ./ ./app
WORKDIR ./app

#Install default Java 11

RUN apt update
RUN apt install -y default-jdk
RUN pip3 install -r requirements.txt
RUN wget https://sourceforge.net/projects/dbpedia-spotlight/files/spotlight/dbpedia-spotlight-1.0.0.jar
RUN wget -O en.tar.gz http://downloads.dbpedia.org/repo/dbpedia/spotlight/spotlight-model/2020.11.18/spotlight-model_lang%3den.tar.gz
RUN tar xzf en.tar.gz
RUN rm en.tar.gz
RUN java jar dbpedia-spotlight-1.0.0.jar en http://localhost:2222/rest & python3 app.py ;
