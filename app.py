"""app.py

Wrapping Spacy NLP to extract tokens, tags, lemmas, sentences, chunks and named
entities.

Usage:

$ python app.py -t example-mmif.json out.json
$ python app.py [--develop]

The first invocation is to just test the app without running a server. The
second is to start a server, which you can ping with

$ curl -H "Accept: application/json" -X POST -d@example-mmif.json http://0.0.0.0:5000/

With the --develop option you get a FLask server running in development mode,
without it Gunicorn will be used for a more stable server.

Normally you would run this in a Docker container, see README.md.

"""

import argparse
from typing import Union

import spacy
from clams.app import ClamsApp
from clams.restify import Restifier
from lapps.discriminators import Uri
from mmif.serialize import Mmif
from mmif.vocabulary import DocumentTypes
from spacy.tokens import Doc


class SpacyWrapper(ClamsApp):

    def __init__(self):
        super().__init__()
        # Load small English core model
        self.nlp = spacy.load("en_core_web_sm")

    def _appmetadata(self):
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:
        for doc in mmif.get_documents_by_type(DocumentTypes.TextDocument):
            in_doc = None
            tok_idx = {}
            if 'pretokenized' in parameters and parameters['pretokenized']:
                for view in mmif.get_views_for_document(doc.id):
                    if Uri.TOKEN in view.metadata.contains:
                        tokens = [token.properties['text'] for token in view.get_annotations(Uri.TOKEN)]
                        tok_idx = {i: f'{view.id}:{token.id}'
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
            self.sign_view(view)
            for attype in (Uri.TOKEN, Uri.POS, Uri.LEMMA,
                           Uri.NCHUNK, Uri.SENTENCE, Uri.NE):
                view.new_contain(attype, document=did)

            for n, tok in enumerate(in_doc):
                a = view.new_annotation(Uri.TOKEN)
                if n not in tok_idx:
                    a.add_property('start', tok.idx)
                    a.add_property('end', tok.idx + len(tok.text))
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

        return mmif


def test(infile, outfile):
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
        test(parsed_args.infile, parsed_args.outfile)
    else:
        # create the app instance
        app = SpacyWrapper()

        http_app = Restifier(app, port=int(parsed_args.port)
        )
        if parsed_args.production:
            http_app.serve_production()
        else:
            http_app.run()
