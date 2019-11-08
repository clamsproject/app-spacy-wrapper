import spacy
from clams.serve import ClamApp
from clams.serialize import *
from clams.vocab import AnnotationTypes
from clams.vocab import MediaTypes
from clams.restify import Restifier
from lapps.discriminators import Uri  # TODO move to clams

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")


class Spacy(ClamApp):
    def appmetadata(self):
        metadata = {
            "name": "Spacy Wrapper",
            "description": "This tool applies spacy tools to the transcript.",
            "vendor": "Team CLAMS",
            "requires": [MediaTypes.T],
            "produces": [AnnotationTypes.OCR],
        }
        return metadata

    def sniff(self, mmif):
        # this mock-up method always returns true
        return True

    def annotate(self, mmif):
        if type(mmif) is not Mmif:
            mmif = Mmif(mmif)
        transcript = ""
        ##load transcript
        transcript_location = mmif.get_medium_location(MediaTypes.T)
        try:
            with open(transcript_location) as transcript_file:
                transcript = transcript_file.read()
        except Exception as e:
            #TODO handle error
            print("ERROR", e)

        ##apply spacy to transcript
        spacy_output = nlp(transcript)

        new_view = mmif.new_view()
        new_view.new_contain(Uri.TOKEN, "SpacyNLP")
        new_view.new_contain(Uri.POS, "SpacyNLP")
        new_view.new_contain(Uri.LEMMA, "SpacyNLP")
        new_view.new_contain(Uri.NCHUNK, "SpacyNLP")
        new_view.new_contain(Uri.SENTENCE, "SpacyNLP")
        new_view.new_contain(Uri.NE, "SpacyNLP")
        # to keep track of char offsets of all tokens
        tok_idx = {}
        for (n, tok) in enumerate(spacy_output):
            pos = tok.tag_
            lemma = tok.lemma_
            p1 = tok.idx
            p2 = p1 + len(tok.text)
            a = new_view.new_annotation("tok_" + str(n))
            a.attype = Uri.TOKEN
            a.start = p1
            a.end = p2
            tok_idx[n] = (p1, p2)
            a.add_feature("pos", pos)
            a.add_feature("lemma", lemma)
            a.add_feature("text", tok.text)
        for (n, chunk) in enumerate(spacy_output.noun_chunks):
            a = new_view.new_annotation("nchunk_" + str(n))
            a.attype = Uri.NCHUNK
            a.start = tok_idx[chunk.start][0]
            a.end = tok_idx[chunk.end - 1][1]
            a.add_feature("text", chunk.text)
        for (n, sent) in enumerate(spacy_output.sents):
            a = new_view.new_annotation("s_" + str(n))
            a.attype = Uri.SENTENCE
            a.start = tok_idx[sent.start][0]
            a.end = tok_idx[sent.end - 1][1]
            a.add_feature("text", sent.text)
        for (n, ent) in enumerate(spacy_output.ents):
            a = new_view.new_annotation("ne_" + str(n))
            a.attype = Uri.NE
            a.start = tok_idx[ent.start][0]
            a.end = tok_idx[ent.end - 1][1]
            a.add_feature("text", ent.text)
            a.add_feature("category", ent.label_)
        contain.producer = self.__class__

        for contain in new_view.contains.keys():
            mmif.contains.update({contain: new_view.id})
        return mmif


if __name__ == "__main__":
    spacy_tool = Spacy()
    spacy_service = Restifier(spacy_tool)
    spacy_service.run()
