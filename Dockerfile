FROM clamsproject/clams-python:0.5.1

WORKDIR ./app

RUN pip install spacy==3.1.2
RUN python -m spacy download en_core_web_sm

COPY ./ ./

CMD ["python", "app.py"]
