import spacy
from spacy.tokens import DocBin

# Blank English model start
nlp = spacy.blank("en")

# Training data format: text + entities with start, end positions and label
TRAIN_DATA = [
    ("Python and Machine Learning skills required", {"entities": [(0, 6, "SKILL"), (11, 28, "SKILL")]}),
    ("Experience with Spark, SQL and Power BI", {"entities": [(16, 21, "SKILL"), (23, 26, "SKILL"), (31, 38, "SKILL")]}),
    # Add more labeled sentences here based on your JD and resumes
]

db = DocBin()

for text, annot in TRAIN_DATA:
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annot.get("entities"):
        span = doc.char_span(start, end, label=label)
        if span:
            ents.append(span)
    doc.ents = ents
    db.add(doc)

db.to_disk("train.spacy")

print("Training data saved to train.spacy")
