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
import os
import urllib.request

import spacy
from clams.app import ClamsApp
from clams.appmetadata import AppMetadata
from clams.restify import Restifier
from lapps.discriminators import Uri
from mmif.serialize import Mmif
from mmif.vocabulary import DocumentTypes
from spacy.tokens import Doc

# Load small English core model
nlp = spacy.load("en_core_web_sm")

APP_VERSION = '0.0.8'
APP_LICENSE = 'Apache 2.0'
MMIF_VERSION = '0.4.0'
SPACY_VERSION = '3.1.2'
SPACY_LICENSE = 'MIT'


# We need this to find the text documents in the documents list
TEXT_DOCUMENT = os.path.basename(str(DocumentTypes.TextDocument))

DEBUG = False


class SpacyApp(ClamsApp):

    def _appmetadata(self):
        metadata = AppMetadata(
            identifier='https://apps.clams.ai/spacy_nlp',
            url='https://github.com/clamsproject/app-spacy-nlp',
            name="spaCy NLP",
            description="Apply spaCy NLP to all text documents in a MMIF file.",
            app_version=APP_VERSION,
            app_license=APP_LICENSE,
            analyzer_version=SPACY_VERSION,
            analyzer_license=SPACY_LICENSE,
        )
        metadata.add_input(DocumentTypes.TextDocument)
        metadata.add_input(Uri.TOKEN, required=False)
        
        metadata.add_parameter(
            name='pretokenized',
            description='Boolean parameter to set the app to use existing tokenization, if available, for text documents for NLP processing. Useful to process ASR documents, for example.',
            type='boolean',
            default=False,
        )
        
        metadata.add_output(Uri.TOKEN)
        metadata.add_output(Uri.POS)
        metadata.add_output(Uri.LEMMA)
        metadata.add_output(Uri.NCHUNK)
        metadata.add_output(Uri.SENTENCE)
        metadata.add_output(Uri.NE)
        return metadata

    def _annotate(self, mmif, **kwargs):
        
        for doc in mmif.get_documents_by_type(DocumentTypes.TextDocument):
            in_doc = None
            tok_idx = {}
            if 'pretokenized' in kwargs and kwargs['pretokenized']:
                for view in mmif.get_views_for_document(doc.id):
                    if Uri.TOKEN in view.metadata.contains:
                        tokens = [token.properties['text'] for token in view.get_annotations(Uri.TOKEN)]
                        tok_idx = {i: f'{view.id}:{token.id}'
                                   for i, token in enumerate(view.get_annotations(Uri.TOKEN))}
                        in_doc = Doc(nlp.vocab, tokens)
                        nlp.add_pipe("sentencizer")
                        for _, component in nlp.pipeline:
                            in_doc = component(in_doc)
            if in_doc is None:
                in_doc = doc.text_value if not doc.location else urllib.request.urlopen(doc.location).read().decode('utf8')
                in_doc = nlp(in_doc)

            did = f'{doc.parent}:{doc.id}' if doc.parent else doc.id
            view = mmif.new_view()
            self.sign_view(view)
            for attype in (Uri.TOKEN, Uri.POS, Uri.LEMMA,
                           Uri.NCHUNK, Uri.SENTENCE, Uri.NE):
                view.new_contain(attype, document=did)

            # def add_annotation(view, attype, identifier, doc_id, start, end, properties):

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
    the annotate() method on the SpacyApp class. Prints a summary of the views
    in the end result."""
    print(SpacyApp().appmetadata(pretty=True))
    with open(infile) as fh_in, open(outfile, 'w') as fh_out:
        mmif_out_as_string = SpacyApp().annotate(fh_in.read(), pretty=True)
        mmif_out = Mmif(mmif_out_as_string)
        fh_out.write(mmif_out_as_string)
        for view in mmif_out.views:
            print("<View id=%s annotations=%s app=%s>"
                  % (view.id, len(view.annotations), view.metadata['app']))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test',  action='store_true', help="bypass the server")
    parser.add_argument('--develop',  action='store_true', help="start a development server")
    parser.add_argument('infile', nargs='?', help="input MMIF file")
    parser.add_argument('outfile', nargs='?', help="output file")
    args = parser.parse_args()

    if args.test:
        test(args.infile, args.outfile)
    else:
        app = SpacyApp()
        service = Restifier(app)
        if args.develop:
            service.run()
        else:
            service.serve_production()
