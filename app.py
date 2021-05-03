"""app.py

Wrapping Spacy NLP to extract tokens, tags, lemmas, sentences, chunks and named
entities.

Usage:

$ python app.py -t example-mmif.json out.json
$ python app.py
$ python app.py --dbpedia

The first invocation is to just test the app without running a Flask server and
without attempting to link entities to DBPedia. The second and third are to
start the Flask server, which you can ping with

$ curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/

With the --dbpedia option the app will attempt to link entities to DBPedia.

Normally you would run this in a Docker container, see README.md.

"""

import os
import sys
import collections
import json
import urllib

import spacy


from clams.app import ClamsApp
from clams.restify import Restifier

from mmif.serialize import *
from mmif.vocabulary import AnnotationTypes
from mmif.vocabulary import DocumentTypes

from lapps.discriminators import Uri

# Load small English core model
nlp = spacy.load("en_core_web_sm")

# default is to not attempt linking to DBPedia
dbpedia = False

# We need this to find the text documents in the documents list
TEXT_DOCUMENT = os.path.basename(DocumentTypes.TextDocument.value)

DEBUG = False


class SpacyApp(ClamsApp):

    def _appmetadata(self):
        return {
           "name": "Spacy Wrapper",
            "app": 'https://apps.clams.ai/spacy_nlp',
            "wrapper_version": "0.0.5",
            "tool-version": "3.0.3",
            "mmif-version": "0.3.0",
            "mmif-python-version": "0.3.1",
            "clams-python-version": "0.2.2",
            "description": "Apply spaCy NLP to all text documents in an MMIF file.",
            "vendor": "Team CLAMS",
            "parameters": {},
            "requires": [{"@type": DocumentTypes.TextDocument.value}],
            "produces": [{"@type": Uri.TOKEN}, {"@type": Uri.POS}, {"@type": Uri.LEMMA},
                         {"@type": Uri.NCHUNK}, {"@type": Uri.SENTENCE}, {"@type": Uri.NE}]
        }

    def _annotate(self, mmif, **kwargs):
        Identifiers.reset()
        self.mmif = mmif if type(mmif) is Mmif else Mmif(mmif)
        for doc in text_documents(self.mmif.documents):
            new_view = self._new_view(doc.id)
            self._add_tool_output(doc, new_view)
        for view in list(self.mmif.views):
            docs = self.mmif.get_documents_in_view(view.id)
            if docs:
                new_view = self._new_view()
                for doc in docs:
                    doc_id = view.id + ':' + doc.id
                    self._add_tool_output(doc, new_view, doc_id=doc_id)
        return self.mmif

    def _new_view(self, docid=None):
        view = self.mmif.new_view()
        view.metadata.app = self.metadata['app']
        properties = {} if docid is None else {'document': docid}
        for attype in (Uri.TOKEN, Uri.POS, Uri.LEMMA,
                       Uri.NCHUNK, Uri.SENTENCE, Uri.NE):
            view.new_contain(attype, properties)
        return view

    def _read_text(self, textdoc):
        """Read the text content from the document or the text value."""
        if textdoc.location:
            fh = urllib.request.urlopen(textdoc.location)
            text = fh.read().decode('utf8')
        else:
            text = textdoc.properties.text.value
        if DEBUG:
            print('>>> %s%s' % (text.strip()[:100],
                                ('...' if len(text) > 100 else '')))
        return text

    def _add_tool_output(self, doc, view, doc_id=None):
        spacy_doc = nlp(self._read_text(doc))
        dbpedia_ents = {}
        if dbpedia:
            dbpedia_ents = {d.text:d.kb_id_ for d in spacy_doc.spans['dbpedia_ents']}
        # keep track of char offsets of all tokens
        tok_idx = {}
        for (n, tok) in enumerate(spacy_doc):
            p1 = tok.idx
            p2 = p1 + len(tok.text)
            tok_idx[n] = (p1, p2)
            add_annotation(
                view, Uri.TOKEN, Identifiers.new("t"),
                doc_id, p1, p2,
                { "pos": tok.tag_, "lemma": tok.lemma_, "text": tok.text })
        for (n, chunk) in enumerate(spacy_doc.noun_chunks):
            add_annotation(
                view, Uri.NCHUNK, Identifiers.new("nc"),
                doc_id, tok_idx[chunk.start][0], tok_idx[chunk.end - 1][1],
                { "text": chunk.text })
        for (n, sent) in enumerate(spacy_doc.sents):
            add_annotation(
                view, Uri.SENTENCE, Identifiers.new("s"),
                doc_id, tok_idx[sent.start][0], tok_idx[sent.end - 1][1],
                { "text": sent.text })
        for (n, ent) in enumerate(spacy_doc.ents):
            try:
                add_annotation(
                    view, Uri.NE, Identifiers.new("ne"),
                    doc_id, tok_idx[ent.start][0], tok_idx[ent.end - 1][1],
                    { "text": ent.text, "category": ent.label_, "kb_id": dbpedia_ents[ent.text]})
            except KeyError:
                add_annotation(
                    view, Uri.NE, Identifiers.new("ne"),
                    doc_id, tok_idx[ent.start][0], tok_idx[ent.end - 1][1],
                    {"text": ent.text, "category": ent.label_})

    def print_documents(self):
        for doc in self.mmif.documents:
            print("%s %s location=%s text=%s" % (
                doc.id, doc.at_type, doc.location, doc.properties.text.value))


def text_documents(documents):
    """Utility method to get all text documents from a list of documents."""
    return [doc for doc in documents if doc.at_type.endswith(TEXT_DOCUMENT)]
    # TODO: replace with the following line and remove TEXT_DOCUMENT variable
    # when mmif-python is updated
    # return [doc for doc in documents if doc.is_type(DocumentTypes.TextDocument)]


def add_annotation(view, attype, identifier, doc_id, start, end, properties):
    """Utility method to add an annotation to a view."""
    a = view.new_annotation(identifier, attype)
    if doc_id is not None:
        a.add_property('document', doc_id)
    a.add_property('start', start)
    a.add_property('end', end)
    for prop, val in properties.items():
        a.add_property(prop, val)


class Identifiers(object):

    """Utility class to generate annotation identifiers. You could, but don't have
    to, reset this each time you start a new view. This works only for new views
    since it does not check for identifiers of annotations already in the list
    of annotations."""

    identifiers = collections.defaultdict(int)

    @classmethod
    def new(cls, prefix):
        cls.identifiers[prefix] += 1
        return "%s%d" % (prefix, cls.identifiers[prefix])

    @classmethod
    def reset(cls):
        cls.identifiers = collections.defaultdict(int)



def test():
    """Run spacy on an input MMIF file. This bypasses the server and just pings
    the annotate() method on the SpacyApp class. Prints a summary of the views
    in the end result."""
    with open(sys.argv[2]) as fh_in, open(sys.argv[3], 'w') as fh_out:
        mmif_out_as_string = SpacyApp().annotate(fh_in.read(), pretty=True)
        mmif_out = Mmif(mmif_out_as_string)
        fh_out.write(mmif_out_as_string)
        for view in mmif_out.views:
            print("<View id=%s annotations=%s app=%s>"
                  % (view.id, len(view.annotations), view.metadata['app']))


if __name__ == "__main__":

    if len(sys.argv) > 3 and '-t' in sys.argv:
        test()
    else:
        if '--dbpedia' in sys.argv:
            dbpedia = True
            nlp.add_pipe(
                'dbpedia_spotlight',
                config={'overwrite_ents':False,
                        'dbpedia_rest_endpoint': 'http://localhost:2222/rest'})
        app = SpacyApp()
        service = Restifier(app)
        service.run()
