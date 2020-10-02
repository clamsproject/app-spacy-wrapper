"""test.py

Run spacy on an input MMIF file. Bypasses the server and just pings the
annotate() method on the Spacy class.

Usage example:

$ python test.py example-mmif.json out.json

"""

import sys
import pprint
import json

from app import Spacy

mmif_in = open(sys.argv[1]).read()
mmif_out = Spacy().annotate(mmif_in)

with open(sys.argv[2], 'w') as fh:
    fh.write(mmif_out.serialize(pretty=True))

for view in mmif_out.views:
    print("<View id=%s annotations=%s app=%s>"
          % (view.id, len(view.annotations), view.metadata['app']))
