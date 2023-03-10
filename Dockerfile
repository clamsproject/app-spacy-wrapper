FROM clamsproject/clams-python:0.5.2

WORKDIR ./app
COPY ./ ./
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
