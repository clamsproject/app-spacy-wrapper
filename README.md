# Spacy NLP Service

The spaCy NLP tool wrapped as a CLAMS service, spaCy is distributed under the [MIT license](https://github.com/explosion/spaCy/blob/master/LICENSE).

This requires Python 3.8 or higher. For local install of required Python modules see [requirements.txt](requirements.txt).

## Using this service

Use `python app.py -t example-mmif.json out.json` just to test the wrapping code without using a server. To test this using a server you run the app as a service in one terminal:

```bash
$ python app.py
```

And poke at it from another:

```bash
$ curl http://0.0.0.0:5000/
$ curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/
```

In CLAMS you usually run this in a container. To create an image

```bash
$ docker build -f Containerfile -t clams-spacy-wrapper .
```

And to run it as a container:

```bash
$ docker run --rm -d -p 5000:5000 clams-spacy-wrapper
$ curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/
```

The spaCy code will run on each text document in the input MMIF file. The file `example-mmif.json` has one text document in the top level `documents` property and two text documents in one of the views. The text documents all look as follows:

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
Instead of a `text:@value` property the text could in an external file, which would be given as a URI in the `location` property. See the readme file in [https://github.com/clamsproject/app-nlp-example](https://github.com/clamsproject/app-nlp-example) on how to do this.