# coding: utf-8
import io
import re
import csv
import math
import nltk
import random
from normality import slugify, collapse_spaces

CLEANUP = r'^\W*((mr|ms|miss|the|of|de)\.?\s+)?(?P<term>.*?)([\'’]s)?\W*$'
CLEANUP = re.compile(CLEANUP, re.I | re.U)


def cleanup_text(text):
    if text is None:
        return
    match = CLEANUP.match(text)
    if match is not None:
        term = match.group('term')
        return collapse_spaces(term)


def text_features(text):
    tokens = re.split(r'\s+', text)
    lower = [slugify(t, sep='') for t in tokens]
    features = {
        'numTokens': len(tokens),
        # '_debug': text,
    }

    for bucket in range(0, 30, 8):
        features['len(>%s)' % bucket] = len(text) > bucket

    for i, token in enumerate(tokens):
        section = 'token[%s]' % i
        word = lower[i] or token
        features['contains(%s)' % word] = True
        features[section] = word
        features[section + 'length'] = len(word)

        # for special in re.findall('\W+', token):
        #     features[section + 'special'] = True

        if lower[i] and token.upper() == token:
            features[section + 'upper'] = True
        if lower[i] and token.lower() == token:
            features[section + 'lower'] = True
        if lower[i] and token.capitalize() == token:
            features[section + 'cap'] = True

    features['lastToken'] = tokens[-1].lower()
    # features['lastWord'] = lower[-1]

    words = [w for w in lower if w is not None and len(w)]
    for bigram in nltk.ngrams(words, 2):
        bigram = ' '.join(bigram)
        features['bigram(%s)' % bigram] = True
    # print(features)
    return features


featuresets = []
tests = []
with io.open('training/entities.csv', 'r', encoding='utf-8', newline='') as fh:
    for row in csv.DictReader(fh):
        text = row.get('text')
        # print(text, '->', cleanup_text(text))
        text = cleanup_text(text)
        if text is None:
            continue
        judgement = row.get('judgement').strip().lower()
        if judgement in ('t', 'f'):
            featuresets.append((text_features(text), judgement))
        else:
            tests.append(text)

random.shuffle(featuresets)

splitter = math.floor(len(featuresets) / 4)
train_set = featuresets[splitter:]
test_set = featuresets[:splitter]
# train_set = featuresets
print("Training set: %s" % len(train_set))
classifier = nltk.NaiveBayesClassifier.train(train_set)

# print(nltk.classify.accuracy(classifier, test_set))
# classifier.show_most_informative_features(20)

for test in tests:
    judgement = classifier.prob_classify(text_features(test))
    if judgement.max() == 'f':
        print(test)
