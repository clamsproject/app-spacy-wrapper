"""app.py

Wrapping Spacy NLP to extract tokens, tags, lemmas, sentences, chunks and named
entities.

"""

import os
import collections
import json

import spacy

from clams.serve import ClamsApp
from clams.restify import Restifier

from mmif.serialize import *
from mmif.vocabulary import AnnotationTypes
from mmif.vocabulary import DocumentTypes

from lapps.discriminators import Uri  # TODO move to clams

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

# We need this to find the text documents in the documents list
TEXT_DOCUMENT = os.path.basename(DocumentTypes.TextDocument.value)

DEBUG = False


class SpacyApp(ClamsApp):

    def __init__(self):
        self.metadata = {
            "name": "Spacy Wrapper",
            "app": 'https://tools.clams.ai/spacy_nlp',
            "wrapper_version": "0.0.2",
            "tool_version": "2.3.2",
            "mmif-spec-version": "0.2.1",
            "mmif-sdk-version": "0.2.0",
            "description": "This tool applies spacy tools to all text documents in an MMIF file.",
            "vendor": "Team CLAMS",
            "requires": [DocumentTypes.TextDocument.value],
            "produces": [Uri.TOKEN, Uri.POS, Uri.LEMMA, Uri.NCHUNK, Uri.SENTENCE, Uri.NE],
        }

    def appmetadata(self):
        return json.dumps(self.metadata)

    def sniff(self, mmif):
        # this mock-up method always returns true
        return True

    def annotate(self, mmif):
        Identifiers.reset()
        self.mmif = mmif if type(mmif) is Mmif else Mmif(mmif)
        # process the text documents in the documents list
        for doc in text_documents(self.mmif.documents):
            new_view = self._new_view(doc.id)
            self._add_tool_output(doc, new_view)
        # process the text documents in all the views, we copy the views into a
        # list because self.mmif.views will be changed
        for view in list(self.mmif.views):
            docs = self.mmif.get_documents_in_view(view.id)
            if docs:
                new_view = self._new_view()
                for doc in docs:
                    doc_id = view.id + ':' + doc.id
                    self._add_tool_output(doc, new_view, doc_id=doc_id)
        return str(self.mmif)

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
            with open(textdoc.location) as fh:
                text = fh.read()
        else:
            text = textdoc.properties.text.value
        if DEBUG:
            print('>>> %s%s' % (text.strip()[:100],
                                ('...' if len(text) > 100 else '')))
        return text

    def _add_tool_output(self, doc, view, doc_id=None):
        spacy_doc = nlp(self._read_text(doc))
        # index to keep track of char offsets of all tokens
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
            add_annotation(
                view, Uri.NE, Identifiers.new("ne"),
                doc_id, tok_idx[ent.start][0], tok_idx[ent.end - 1][1],
                { "text": ent.text, "category": ent.label_ })

    def print_documents(self):
        for doc in self.mmif.documents:
            print("%s %s location=%s text=%s" % (
                doc.id, doc.at_type, doc.location, doc.properties.text.value))


def text_documents(documents):
    """Utility method to get all text documents from a list of documents."""
    return [doc for doc in documents if doc.at_type.endswith(TEXT_DOCUMENT)]


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


if __name__ == "__main__":

    app = SpacyApp()
    service = Restifier(app)
    service.run()
