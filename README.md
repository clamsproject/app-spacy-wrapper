# Spacy NLP Service

The spaCy NLP tool wrapped as a CLAMS service, spaCy is distributed under the [MIT license](https://github.com/explosion/spaCy/blob/master/LICENSE).

This requires Python 3.6 or higher. For local install of required Python modules do:

```bash
$ pip install clams-python==0.4.4
$ pip install click==7.1.1
$ pip install lapps==0.0.2
$ pip install spacy==3.0.3
$ pip install spacy-dbpedia-spotlight==0.2.0
$ python -m spacy download en_core_web_sm
```

A more recent version of spaCy most likely will work too. The installation of `click==7.1.1` is added because `clams-python==0.4.3` installs version 8.0.1, which is incompatible with the version needed by spaCy (because version 8.0.1 removes `click._bashcomplete`).

## Using this service

Use `python app.py -t example-mmif.json out.json` just to test the wrapping code without using a server. To test this using a server you run the app as a service in one terminal (when you add the optional  `--develop` parameter a Flask server will be used in development mode, otherwise you will get a production Gunicorn server):

```bash
$ python app.py [--develop]
```

And poke at it from another:

```bash
$ curl http://0.0.0.0:5000/
$ curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/
```

In CLAMS you usually run this in a Docker container. To create a Docker image

```
$ docker build -t clams-spacy-nlp .
```

And to run it as a container:

```bash
$ docker run --rm -d -p 5000:5000 clams-spacy-nlp
$ curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/
```

The spaCy code will run on each text document in the input. The example file `example-mmif.json` has one text document in the top level `documents` property and two text documents in one of the views. The text documents all look as follows:

```json
{
  "@type": "http://mmif.clams.ai/0.4.0/vocabulary/TextDocument",
  "properties": {
    "id": "m2",
    "text": {
      "@value": "Hello, this is Jim Lehrer with the NewsHour on PBS...."
    }
  }
}
```
Instead of a `text:@value` property the text could in an external file, which would be given as a URI in the `location` property.

## Entity Linking

Code for entity linking is in progress. To run the local server do

```bash
$ python app.py --dbpedia
```

For building a Docker image use `Dockerfile-dbpedia`.

```bash
$ docker build -f Dockerfile-dbpedia -t clams-spacy-nlp-linking .
```

Neither of these work at the moment.