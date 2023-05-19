import re

from clams.appmetadata import AppMetadata
from lapps.discriminators import Uri
from mmif import DocumentTypes


# DO NOT CHANGE the function name 
def appmetadata() -> AppMetadata:
    metadata = AppMetadata(
        name="CLAMS wrapper for spaCy NLP",
        description="Apply spaCy NLP to all text documents in a MMIF file.",
        app_license="Apache 2.0",
        identifier=f"http://apps.clams.ai/spacy-wrapper",
        url='https://github.com/clamsproject/app-spacy-wrapper',
        analyzer_version=[l.strip().rsplit('==')[-1] for l in open('requirements.txt').readlines() if re.match(r'^spacy==', l)][0],
        analyzer_license='MIT',
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


# DO NOT CHANGE the main block
if __name__ == '__main__':
    import sys
    sys.stdout.write(appmetadata().jsonify(pretty=True))
