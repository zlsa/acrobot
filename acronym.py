#!/bin/env python3

def lerp(il, i, ih, ol, oh):
  return ((i - il) / (ih - il)) * (oh - ol) + ol

import re
import json

CONFIDENCE_FACTOR_LENGTH = [
  0,
  0.3,
  0.7,
  1.2,
  3,
  5,
  8,
  8,
  12,
  25,
  40
]

fac = 0.1

WORDLIST = {
  z[1]: lerp(23135851162 ** fac, int(z[0]) ** fac, 5056310 ** fac, 1, 0)
  for z in [x.strip().split(':') for x in open('words.txt', 'r')]
}

class Definition:

  def __init__(self, json=None):
    self.acronym = None
    self.definition = ''

    if json: self.read(json)

  def write(self):

    json = {
      'definition': self.definition
    }

    return json

  def read(self, json):
    self.definition = json['definition']

class Acronym:

  def __init__(self, json=None):
    self.abbreviations = []

    self.definitions = []

    if json: self.read(json)

  def read(self, json):
    self.abbreviations = []
    self.definitions = []

    for abbreviation in json['abbreviations']:
      self.addAbbreviation(abbreviation)

    for definition in json['definitions']:
      self.addDefinition(Definition(definition))

  def hasAbbreviation(self, abbreviation):
    return abbreviation in self.abbreviations

  def write(self):

    json = {}

    json['abbreviations'] = self.abbreviations
    json['definitions'] = [d.write() for d in self.definitions]

    return json

  def addAbbreviation(self, abbreviation):
    if abbreviation not in self.abbreviations:
      self.abbreviations.append(abbreviation)

  def addDefinition(self, definition):
    definition.acronym = self
    self.definitions.append(definition)

  def getFallbackText(self):
    return ', '.join([x.upper() for x in self.abbreviations]) + ': ' + ', '.join([x.definition for x in self.definitions])

class Manager:

  def __init__(self):
    self.acronyms = []

  def read(self, json):
    acronyms = json['acronyms']
    
    for acronym in acronyms:
      self.acronyms.append(Acronym(acronym))

  def write(self):
    json = {}

    acronyms = [acronym.write() for acronym in self.acronyms]

    json['acronyms'] = acronyms
    
    return json

  def readFromFile(self, filename):
    self.read(json.load(open(filename, 'r')))
    print('read ' + str(len(self.acronyms)) + ' acronyms')

  def writeToFile(self, filename):
    json.dump(self.write(), open(filename, 'w'))
    print('wrote ' + str(len(self.acronyms)) + ' acronyms')

  def getAcronym(self, abbreviation):

    abbreviation = abbreviation.lower()
    
    for acronym in self.acronyms:
      if acronym.hasAbbreviation(abbreviation):
        return acronym

    return None

  def addAcronym(self, abbreviation, definition):
    acronym = self.getAcronym(abbreviation)

    if not acronym:
      acronym = acronym.Acronym()
      acronym.addAbbreviation(abbreviation)
      self.acronyms.append(acronym)
      
    acronym.addDefinition(definition)

  def abbreviationConfidence(self, word):
    if not self.getAcronym(word): return 0

    length_weight_factor = CONFIDENCE_FACTOR_LENGTH[min(len(word), 10)]
    capitalization_factor = sum(1 for c in word if not c.islower())
    word_factor = 1

    word = word.lower()

    if word in WORDLIST:
      word_factor = 1 - WORDLIST[word]

    confidence = (capitalization_factor + 1) * length_weight_factor * word_factor
    
    return confidence

  def extract(self, text, force):
    words = re.findall(r"[\w\-]+", text)

    acronyms = []

    total_confidence = 0

    for word in words:
      acronym = self.getAcronym(word)

      if acronym:
        confidence = self.abbreviationConfidence(word)
        total_confidence += confidence
        acronyms.append((word, acronym, confidence))
      elif force:
        acronyms.append((word, None, 0))

    return (acronyms, total_confidence)

if __name__ == '__main__':
  manager = Manager()
  manager.readFromFile('acronyms.json')

  words = [
    'see',
    'los',
    'LOS',
    'ocisly'
  ]

  for w in words:
    print(w + ': ' + str(manager.abbreviationConfidence(w)))
  
