import sys
from app import Spacy

tool = Spacy()
a = open(sys.argv[1])
b = a.read()
c = tool.annotate(b)
with open (sys.argv[2], "w") as out:
    out.write(str(c))
# for i in c.views:
#     a = i.__dict__
#     print (a)
#     c = a.get("contains")
#     bd = a.get("annotations")
#     for d in bd:
#         print (d.__dict__)
