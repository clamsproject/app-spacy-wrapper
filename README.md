# Spacy NLP Service

The spaCy NLP tool wrapped as a CLAMS service, spaCy is distributed under the [MIT license](https://github.com/explosion/spaCy/blob/master/LICENSE).

This requires Python 3.6 or higher. For local install of required Python modules do:

```bash
$ pip install clams-python==0.5.1
$ pip install spacy==3.3.1
```

In an earlier version of this application we had to manually install click==7.1.1 because clams-python installed version 8.0.1 and spaCy was not compatible with that version. The spacy install now does that automatically.

You also need the small spaCy model. Even if you have already download a model named `en_core_web_sm` with the older version of spaCy, it is important that you run the following command, because different versions of spaCy use the name `en_core_web_sm` to refer to slightly different models.

```bash
$ python -m spacy download en_core_web_sm
```

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

```bash
$ docker build -t clams-spacy-nlp .
```

And to run it as a container:

```bash
$ docker run --rm -d -p 5000:5000 clams-spacy-nlp
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

## Using this service with an uncased NER model

The default spaCy NER (Named Entity Recognition) is optimized for cased input, but is not robust against lowercase input. For example, it could not recognize 'jim lehrer' (lowercase) as a person entity.

As a result, when running `app.py`, an option could be specified so that the NER task is performed by a custom-trained model, optimized for lowercase data (in which we will call it "the uncased model"), while the other NLP tasks (such as POS tagging, lemmatizer, and sentence tokenizer) would still be performed by the default spaCy model.

The uncased model is created by fine-tuning the NER layer of the default spaCy model (`en_core_web_sm`) on the CoNLL 2003 English dataset, after the data is all lowercased. More details on how the uncased model is created could be found in [this repo](https://github.com/JinnyViboonlarp/clams-spacy-tuning-ner).

To test the app **without** the uncased model, run the below command on your terminal. The app would use the default spaCy model (`en-core-web-sm`) to do the NER task.

```
$ python app.py -t example-mmif.json out.json
```

To test the app **with** the uncased model, use this command instead.

```
$ python app.py -t -u example-mmif-uncased.json out-uncased.json
```

## Using this service with a dependency parser

The argument `--dep` tells the spaCy NLP model to do dependency parsing on the input text.

```
$ python app.py -t --dep example-mmif.json out.json
```
