# Spacy NLP Service

The spaCy NLP tool wrapped as a CLAMS service using the following specifications:
- MMIF 0.2.2: [https://mmif.clams.ai/0.2.2](https://mmif.clams.ai/0.2.2)
- mmif-python 0.2.2: [https://pypi.org/project/mmif-python/0.2.2/](https://pypi.org/project/mmif-python/0.2.2/)
- clams-python 0.2.0: [https://pypi.org/project/clams-python/0.2.0/](https://pypi.org/project/clams-python/0.2.0/)

spaCy is available at https://spacy.io/ and is distributed under the [MIT license](https://github.com/explosion/spaCy/blob/master/LICENSE).

This requires Python 3.6 or higher. For local install of Python modules in a clean virtual environment do:

```bash
$> pip install spacy==3.0.3
$> python -m spacy download en_core_web_sm
$> pip install clams-python==0.2.0
$> pip install lapps==0.0.2
```

A more recent version of spaCy most likely will work too.

## Testing and using this service

Use `python app.py -t example-mmif.json out.json` just to test the wrapping code without using Flask. To test this using a Flask server you run the app as a service in one terminal:

```bash
$> python app.py
```

And poke at it from another:

```bash
$> curl http://0.0.0.0:5000/
$> curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/
```

In CLAMS you usually run this in a Docker container. To create a Docker image

```bash
$> docker build -t clams-spacy-nlp .
```

And to run it as a container:

```bash
$> docker run --rm -d -p 5000:5000 clams-spacy-nlp
$> curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/
```

