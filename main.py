import os
import json

from flask import Flask, request
import spacy
from lapps import lif
from lapps.discriminators import Uri

from utils import json_response, JSON_MIME_TYPE
from metadata import METADATA

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')


app = Flask(__name__)


@app.route("/spacy", methods=['GET'])
def metadata():
    return json_response(json.dumps(METADATA))

@app.route("/spacy", methods=['POST'])
def execute():
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)
    doc = nlp(request.json["text"])
    data = build_data_object(request, doc)
    return json_response(json.dumps(data.as_pretty_json()))


def build_data_object(request, doc):
    #entities = [(ent.start, ent.end) for ent in doc.ents]
    container = lif.Container()
    text = request.json["text"]
    container.set_text(text)
    container.set_language("en")
    view = container.new_view("v1")
    view.add_contains(Uri.TOKEN, "SpacyNLP", "en_core_web_sm")
    view.add_contains(Uri.POS, "SpacyNLP", "en_core_web_sm")
    view.add_contains(Uri.LEMMA, "SpacyNLP", "en_core_web_sm")
    view.add_contains(Uri.NCHUNK, "SpacyNLP", "en_core_web_sm")
    view.add_contains(Uri.SENTENCE, "SpacyNLP", "en_core_web_sm")
    view.add_contains(Uri.NE, "SpacyNLP", "en_core_web_sm")
    for (n, tok) in enumerate(doc):
        pos = tok.tag_
        lemma = tok.lemma_
        p1 = tok.idx
        p2 = p1 + len(tok.text)
        a = view.new_annotation("t%d" % (n + 1), Uri.TOKEN, p1, p2)
        a.add_feature('pos', pos)
        a.add_feature('lemma', lemma)
        a.add_feature('text', tok.text)
    # TODO: start and end are not character offsets but token offsets
    # TODO: need to translate to character offsets or refer to token identifiers
    for (n, chunk) in enumerate(doc.noun_chunks):
        a = view.new_annotation("nc%d" % (n + 1), Uri.NCHUNK, chunk.start, chunk.end)
    for (n, sent) in enumerate(doc.sents):
        a = view.new_annotation("s%d" % (n + 1), Uri.SENTENCE, sent.start, sent.end)
    for (n, ent) in enumerate(doc.ents):
        a = view.new_annotation("ne%d" % (n + 1), Uri.NE, ent.start, ent.end)
        a.add_feature('category', ent.label_)
    data = lif.Data(discriminator=Uri.LIF, payload=container)
    return data


if __name__ == '__main__':

    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port, debug=True)
    
