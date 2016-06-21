
import md
import util
import json
from slackclient import SlackClient
import interface

class SlackInterface(interface.Interface):

  TYPE = 'slack'

  def __init__(self, token):
    self.token = token
    super().__init__()

  def init(self):
    self.slack = None

  def _start(self):
    self.slack = SlackClient(self.token)
    
    if not self.slack.rtm_connect():
      raise Exception('could not connect to slack')

  def _poll(self):
    events = [0]
    
    while events:
      events = self.slack.rtm_read()
      for event in events:
        self.handleEvent(event)

  def sendMessage(self, channel, text=None, attachments=[]):
    self.slack.api_call(
      'chat.postMessage', channel=channel, text=text,
      attachments=json.dumps(attachments),
      as_user=True
    )

  def sendDefinitions(self, acronyms, channel):
    if not acronyms:
      self.sendMessage(channel, 'No acronyms found.')
      return
    
    attachments = []

    definition_number = 0
    
    for abbreviation, acronym, confidence in acronyms:
      attachment = {}

      attachment['title'] = abbreviation.upper()
      attachment['mrkdwn_in'] = ['text']
      
      if acronym:
        attachment['fallback'] = acronym.getFallbackText()
        attachment['text'] = '\n'.join([md.toSlack(x.definition) for x in acronym.definitions])
        attachment['color'] = '#ccaa55'
        
        definition_number += len(acronym.definitions)
      else:
        attachment['fallback'] = abbreviation.upper() + ': not found'
        attachment['text'] = 'not found'
        attachment['color'] = 'danger'

      attachments.append(attachment)
      
    self.sendMessage(channel, 'Found ' + str(definition_number) + ' definition' + util.s(definition_number), attachments)
    
  def handleEventMessage(self, event):
    print(event)
    
    user = event['user']
    channel = event['channel']
    text = event['text']

    private = False

    user = self.slack.api_call('users.info', user=user)

    if not user['ok']:
      return False

    print(user)

    if 'user' in user:
      user = user['user']

    if user['is_bot']: return
    
    # if this is a direct chat
    if channel.startswith('D'): private = True
    
    if (not (text.lower().startswith('what') or text.lower().startswith('acrobot')) and not private): return

    self.handleMessage(text, channel, private)

  def handleEvent(self, event):
    if event['type'] == 'message':
      self.handleEventMessage(event)

        
