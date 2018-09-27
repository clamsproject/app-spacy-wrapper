from utils import get_version
from lapps.discriminators import Uri


METADATA =  {

    "name": "Spacy",
    "version": get_version(),
    "vendor": "http:/www.lappsgrid.org",
    "encoding": "UTF-8",
    "allow": Uri.ANY,
    "description": "spaCy NLP -- https://spacy.io/",
    "license": Uri.MIT,

    "requires": {
        "language": [ "en" ],
        "format": [ Uri.TEXT, Uri.LIF ],
        "annotations": [ ] },

    "produces": {
        "language": [ "en" ],
        "format": [ Uri.LIF ],
        "annotations": [ Uri.TOKEN, Uri.POS, Uri.LEMMA, Uri.NCHUNK, Uri.SENTENCE,  Uri.NE ] }
}
