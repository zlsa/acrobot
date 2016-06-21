#!/bin/env python3

import slack
import acronym
import time

import tokens

class Acrobot:

  def __init__(self):
    self.manager = acronym.Manager()
    self.manager.readFromFile('acronyms.json')

    self.interfaces = []
    
    self.manager.writeToFile('acronyms.json')

  def addInterface(self, interface):
    self.interfaces.append(interface)
    interface.acrobot = self

  def poll(self):
    for interface in self.interfaces:
      interface.poll()

if __name__ == '__main__':
  acrobot = Acrobot()
  
  for t in tokens.slack:
    acrobot.addInterface(slack.SlackInterface(t))

  while True:
    acrobot.poll()
    time.sleep(0.1)
