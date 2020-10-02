"""app.py

Wrapping spaCy NLP to extract tokens, tags, lemmas, sentences, chunks and named entities.

"""

import collections

import spacy

from clams.serve import ClamsApp
from clams.restify import Restifier

from mmif.serialize import *
from mmif.vocabulary import AnnotationTypes
from mmif.vocabulary import DocumentTypes

from lapps.discriminators import Uri  # TODO move to clams

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

# example transcript data are on shannon: /data/clams/wgbh/transcripts

# TOD): this should not be needed
TEXT_DOCUMENT = 'TextDocument'


DEBUG = False


class Spacy(ClamsApp):

    def appmetadata(self):
        metadata = {
            "name": "Spacy Wrapper",
            "app": 'https://tools.clams.ai/spacy_nlp',
            "wrapper_version": "1.0.3",
            "tool_version": "2.3.2",
            "description": "This tool applies spacy tools to all text documents in an MMIF file.",
            "mmif-version": "0.2.1",
            "vendor": "Team CLAMS",
            "requires": [DocumentTypes.TextDocument],
            "produces": [Uri.TOKEN, Uri.POS, Uri.LEMMA, Uri.NCHUNK, Uri.SENTENCE, Uri.NE],
        }
        return metadata

    def sniff(self, mmif):
        # this mock-up method always returns true
        return True

    def annotate(self, mmif):
        self.mmif = mmif if type(mmif) is Mmif else Mmif(mmif)
        gdocs = GroupedDocuments(self.mmif)
        if DEBUG:
            self.print_documents()
            gdocs.pp()
        for view_id, textdocs in gdocs:
            if textdocs:
                spacy_view = self.new_spacy_view()
            for textdoc in textdocs:
                text = self.read_text(textdoc)
                doc_id = textdoc.id
                if view_id is not None:
                    doc_id = view_id + ':' + doc_id
                if DEBUG:
                    print('>>> %s%s' % (text.strip()[:100],
                                        ('...' if len(text) > 100 else '')))
                spacy_doc = nlp(text)
                self.add_spacy_elements_to_view(spacy_view, spacy_doc, doc_id)
        return self.mmif

    def new_spacy_view(self):
        view = self.mmif.new_view()
        view.metadata.app = self.appmetadata()['app']
        view.new_contain(Uri.TOKEN)
        view.new_contain(Uri.POS)
        view.new_contain(Uri.LEMMA)
        view.new_contain(Uri.NCHUNK)
        view.new_contain(Uri.SENTENCE)
        view.new_contain(Uri.NE)
        return view

    def read_text(self, textdoc):
        """Read the text content from the document or the text value."""
        # TODO: if a location is specified and the file cannot be opened then
        # this should report an error.
        fname = textdoc.location
        try:
            with open(fname) as fh:
                return fh.read()
        except FileNotFoundError as e:
            return textdoc.properties.text.value

    def add_spacy_elements_to_view(self, view, spacy_doc, doc_id):
        # to keep track of char offsets of all tokens
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


def add_annotation(view, attype, identifier, doc_id, start, end, properties):
    a = view.new_annotation(identifier, attype)
    a.add_property('document', doc_id)
    a.add_property('start', start)
    a.add_property('end', end)
    for prop, val in properties.items():
        a.add_property(prop, val)


class GroupedDocuments(object):

    """Groups all TextDocuments in the MMIF file on the identfier of the view they
    are in. Any textDocument occurring in the documents list will have None as
    the view identifier. The motivation for this grouping is that we create a
    new view for (1) each TextDocument in the documents list and (2) each group
    of TextDocuments in a view."""

    def __init__(self, mmif):
        self.docs = [(None, [doc for doc in mmif.documents
                             if doc.at_type.endswith(TEXT_DOCUMENT)])]
        for view in mmif.views:
            docs = mmif.get_documents_in_view(view.id)
            self.docs.append((view.id, docs))

    def __getitem__(self, i):
        return self.docs[i]

    def pp(self):
        for view_id, docs in self.docs:
            print("%-4s  ==>  %s" % (view_id, ' '.join([doc.id for doc in docs])))


class Identifiers(object):

    identifiers = collections.defaultdict(int)

    @classmethod
    def new(cls, prefix):
        cls.identifiers[prefix] += 1
        return "%s%d" % (prefix, cls.identifiers[prefix])

    @classmethod
    def reset(cls):
        cls.identifiers = collections.defaultdict(int)


if __name__ == "__main__":

    spacy_tool = Spacy()
    spacy_service = Restifier(spacy_tool)
    spacy_service.run()
