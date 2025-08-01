"""
Wrapper for the Python spaCy library.
"""

import argparse
import logging
from typing import Union

import spacy
from spacy.cli import download as spacy_download
from clams import ClamsApp, Restifier
from lapps.discriminators import Uri
from mmif import Mmif, DocumentTypes
from spacy.tokens import Doc


class SpacyWrapper(ClamsApp):

    def __init__(self):
        super().__init__()
        # Load small English core model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError as e:  # spacy raises OSError if model not found
            spacy_download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def _appmetadata(self):
        # see metadata.py
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:

        mmif_obj = mmif if type(mmif) == Mmif else Mmif(mmif)

        for doc in mmif_obj.get_documents_by_type(DocumentTypes.TextDocument):
            in_doc = None
            tok_idx = {}
            if parameters.get('pretokenized') is True:
                for view in mmif_obj.get_views_for_document(doc.id):
                    if Uri.TOKEN in view.metadata.contains:
                        tokens = [token.get_property('text') for token in view.get_annotations(Uri.TOKEN)]
                        tok_idx = {i : f'{view.id}:{token.id}'
                                   for i, token in enumerate(view.get_annotations(Uri.TOKEN))}
                        in_doc = Doc(self.nlp.vocab, tokens)
                        self.nlp.add_pipe("sentencizer")
                        for _, component in self.nlp.pipeline:
                            in_doc = component(in_doc)
            if in_doc is None:
                in_doc = doc.text_value if not doc.location else open(doc.location_path()).read()
                in_doc = self.nlp(in_doc)

            view = mmif.new_view()
            self.sign_view(view, parameters)
            for attype in (Uri.TOKEN, Uri.POS, Uri.LEMMA, Uri.NCHUNK, Uri.SENTENCE, Uri.NE):
                view.new_contain(attype, document=doc.id)

            for n, tok in enumerate(in_doc):
                a = view.new_annotation(Uri.TOKEN)
                if n not in tok_idx:
                    a.add_property("start", tok.idx)
                    a.add_property("end", tok.idx + len(tok))
                    tok_idx[n] = a.id
                else:
                    a.add_property('targets', [tok_idx[n]])
                a.add_property('pos', tok.tag_)
                a.add_property('lemma', tok.lemma_)
                a.add_property('text', tok.text)
            for at_type, segmentations in zip((Uri.NCHUNK, Uri.SENTENCE, Uri.NE),
                                              (in_doc.noun_chunks, in_doc.sents, in_doc.ents)):
                for n, segment in enumerate(segmentations):
                    a = view.new_annotation(at_type)
                    a.add_property('targets', [tok_idx[i] for i in range(segment.start, segment.end)])
                    a.add_property('text', segment.text)
                    if segment.label_:
                        a.add_property('category', segment.label_)
        return mmif_obj


def get_app():
    return SpacyWrapper()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", action="store", default="5000", help="set port to listen")
    parser.add_argument("--production", action="store_true", help="run gunicorn server")

    parsed_args = parser.parse_args()

    # create the app instance
    app = get_app()

    http_app = Restifier(app, port=int(parsed_args.port))
    # for running the application in production mode
    if parsed_args.production:
        http_app.serve_production()
    # development mode
    else:
        app.logger.setLevel(logging.DEBUG)
        http_app.run()
