# Spacy NLP Service


## Description

The spaCy NLP module wrapped as a CLAMS service, spaCy is distributed under the [MIT license](https://github.com/explosion/spaCy/blob/master/LICENSE).


## User instructions

General user instructions for CLAMS apps are available at [CLAMS Apps documentation](https://apps.clams.ai/clamsapp).

### System requirements

This requires Python 3.8 or higher. For local installation of required Python modules see [requirements.txt](requirements.txt).

#### Running as a local python program

To test just the wrapping code without using a server use the following:

```bash
python app.py -t example-mmif.json out.json
```

### Configurable runtime parameters

For the full list of parameters, please refer to the app metadata from in the CLAMS App Directory at [https://apps.clams.ai/#spacy-wrapper](https://apps.clams.ai/#spacy-wrapper) or the [`metadata.py`](metadata.py) file in this repository.

### Input and output details

The spaCy code will run on each text document in the input MMIF file. The file `example-input.json` has one text document in the top level *documents* property and two text documents in one of the views. The output file `example-output.json` has a new view for each of those text documents.
