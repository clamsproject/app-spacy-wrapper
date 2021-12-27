FROM clamsproject/clams-python:0.5.0

WORKDIR ./app

# Using the requirements.txt file in a Docker build crashed the pip install
# process (it does not crash when I run it in OSX, it just says there are
# version incompatibilities). So doing all the installs in separate steps
# because that way it does not crash.
RUN pip install lapps==0.0.2
RUN pip install spacy==3.0.3
RUN python -m spacy download en_core_web_sm

COPY ./ ./

CMD ["python", "app.py"]
