# spaCy CLAMS service with custom NER

In the original [repository](https://github.com/clamsproject/app-spacy-nlp), an off-the-shelf spaCy model is wrapped as a CLAMS service. That model could perform an NER (Named Entity Recognition) task, but it is not robust against lowercase input. For example, it could not recognize 'jim lehrer' (lowercase) as a person entity.

As a result, I edited the code so that the NER task could be specified to be performed by the custom-trained spaCy model trained on lowercased data (which is the same model as `trained_models/model-best-uncased-sm` in [this repository](https://github.com/JinnyViboonlarp/clams-spacy-tuning-ner), while the other NLP tasks (such as POS tagging, lemmatizer, and sentence tokenizer) would still be performed by the all-purpose pretrained spaCy model. The two models are wrapped in the same container, and could add annotations to the same view.

To test the app **without** the custom-trained NER model, run the below command on your terminal. The app would use the spaCy NLP model (`en-core-web-sm`) to do the NER task.

```
$ python app.py -t example-mmif.json out.json
```

To test the app **with** the custom-trained NER model for uncased data, use this command instead. Note that the text data would be uncased before passing through the NER model.

```
$ python app.py -t -u example-mmif.json out-uncased.json
```
