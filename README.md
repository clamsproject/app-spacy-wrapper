# spaCy CLAMS service with custom NER

In the original [repository](https://github.com/clamsproject/app-spacy-nlp), an off-the-shelf spaCy model is wrapped as a CLAMS service. That model could perform an NER (Named Entity Recognition) task, but it is not robust against lowercase input. For example, it could not recognize 'jim lehrer' (lowercase) as a person entity.

As a result, I edited the code so that the NER task would be performed by the custom-trained spaCy model trained on lowercased data (which is the same model as `trained_models/model-best-uncased-sm` in [this repository](https://github.com/JinnyViboonlarp/clams-spacy-tuning-ner), while the other NLP tasks (such as POS tagging, lemmatizer, and sentence tokenizer) would still be performed by the all-purpose pretrained spaCy model. The two models are wrapped in the same container, and could add annotations to the same view.
