"""test.py

Run spacy on an input MMIF file. This bypasses the server and just pings the
annotate() method on the SpacyApp class. Prints a summary of the views in the
end result.

Usage:

$ python test.py example-mmif.json out.json

"""

import sys

from app import SpacyApp

mmif_in = open(sys.argv[1]).read()
mmif_out = SpacyApp().annotate(mmif_in)

with open(sys.argv[2], 'w') as fh:
    fh.write(mmif_out.serialize(pretty=True))

for view in mmif_out.views:
    print("<View id=%s annotations=%s app=%s>"
          % (view.id, len(view.annotations), view.metadata['app']))
