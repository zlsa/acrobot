#!/bin/env python3

import re

def toSlack(md):
  out = md.replace('~~', '~')
  out = re.sub(r'\[(.+)\]\((.+)\)', r'<\2|\1>', out)

  return out

if __name__ == '__main__':
  print(toSlack('~~strikethrough~~ [reddit](google.com)'))
