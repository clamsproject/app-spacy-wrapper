"""
DELETE THIS MODULE STRING AND REPLACE IT WITH A DESCRIPTION OF YOUR APP.

app.py Template

The app.py script does several things:
- import the necessary code
- create a subclass of ClamsApp that defines the metadata and provides a method to run the wrapped NLP tool
- provide a way to run the code as a RESTful Flask service 


"""

import argparse
from typing import Union

# Imports needed for Clams and MMIF.
# Non-NLP Clams applications will require AnnotationTypes

from clams import ClamsApp, Restifier
from mmif import Mmif, View, Annotation, Document, AnnotationTypes, DocumentTypes

# For an NLP tool we need to import the LAPPS vocabulary items
from lapps.discriminators import Uri

# Spacy imports
import spacy
from spacy.tokens import Doc

class SpacyWrapper(ClamsApp):

    def __init__(self):
        super().__init__()
        # load small English core model
        self.nlp = spacy.load("en_core_web_sm")

    def _appmetadata(self):
        # see metadata.py
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:
        if mmif.isinstance(Mmif):
            mmif_obj = mmif
        else:
            mmif_obj = Mmif(mmif)

        for doc in mmif_obj.get_documents_by_type(DocumentTypes.TextDocument):
            in_doc = None
            tok_idx = {}
            if 'pretokenizd' in parameters and parameters['pretokenized']:
                for view in mmif_obj.get_Views_for_document(doc.id):
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
            
            did = f'{doc.parent}:{doc.id}' if doc.parent else doc.id
            view = mmif.new_view()
            self.sign_view(view, parameters)
            for attype in (Uri.TOKEN, Uri.POS, Uri.LEMMA, Uri.NCHUNK, Uri.SENTENCE, Uri.NE):
                view.new_contain(attype, document=did)
            
            for n, tok in enumerate(in_doc):
                a = view.new_annotation(Uri.TOKEN)
                if n not in tok_idx:
                    a.add_property("start", tok.idx)
                    a.add_property("end", tok.idx + len(tok.idx))
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

def _test(infile, outfile):
    """Run spacy on an input MMIF file. This bypasses the server and just pings
    the annotate() method on the SpacyWrapper class. Prints a summary of the views
    in the end result."""
    app = SpacyWrapper()
    print(app.appmetadata(pretty=True))
    with open(infile) as fh_in, open(outfile, 'w') as fh_out:
        mmif_out_as_string = app.annotate(fh_in.read(), pretty=True)
        mmif_out = Mmif(mmif_out_as_string)
        fh_out.write(mmif_out_as_string)
        for view in mmif_out.views:
            print("<View id=%s annotations=%s app=%s>"
                  % (view.id, len(view.annotations), view.metadata['app']))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", action="store", default="5000", help="set port to listen"
    )
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    parser.add_argument('-t', '--test',  action='store_true', help="bypass the server")
    parser.add_argument('infile', nargs='?', help="input MMIF file")
    parser.add_argument('outfile', nargs='?', help="output file")

    parsed_args = parser.parse_args()

    if parsed_args.test:
        _test(parsed_args.infile, parsed_args.outfile)
    else:
        # create the app instance
        app = SpacyWrapper()

        http_app = Restifier(app, port=int(parsed_args.port)
        )
        # for running the application in production mode
        if parsed_args.production:
            http_app.serve_production()
        # development mode
        else:
            http_app.run()
