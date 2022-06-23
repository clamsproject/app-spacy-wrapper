import spacy

if __name__ == '__main__':

    test_sentence = "Hello, this is Jim Lehrer with the NewsHour on PBS. In the nineteen eighties, \
    barking dogs have increasingly become a problem in urban areas.".lower()
    
    ner = spacy.load('ner_models/model-best-uncased-sm')
    nlp = spacy.load("en_core_web_sm")

    print("off-the-shelf model")
    doc = nlp(test_sentence)
    print([(ent.text, ent.label_) for ent in doc.ents])
    # the output: [('pbs', 'ORG'), ('the nineteen eighties', 'DATE')]

    print("trained NER model")
    doc = ner(test_sentence)
    print([(ent.text, ent.label_) for ent in doc.ents])
    # the output: [('hello', 'PER'), ('jim lehrer', 'PER'), ('pbs', 'ORG')]
    
