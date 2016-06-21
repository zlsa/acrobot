
class Interface:

  def __init__(self):
    self.acrobot = None
    
    self.init()

    self.start()

  def start(self):
    self._start()
    print('connected with ' + self.TYPE)

  def init(self):
    raise Exception('do not use Interface() directly')

  def handleMessage(self, text, channel, private=False):
    force = False

    if text.lower().startswith('acrobot'):
      force = True
      text = text.split(None, 1)[1]
      print(text)
    
    acronyms, confidence = self.acrobot.manager.extract(text, force)

    if confidence > 2 or private or force:
      self.sendDefinitions(acronyms, channel)

  def poll(self):
    self._poll()

class DummyInterface(Interface):

  TYPE = 'dummy'

  def _poll(self):
    self.handleMessage('testing 123', 'foo', False)
