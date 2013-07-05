def format_error(msg, key):
   if msg:
      msg = u'{msg}: {key}'.format(msg=msg, key=key)
   else:
      msg = unicode(key)

   return msg.encode('utf-8')

class KeyInsertError(Exception):
   def __init__(self, key, msg=None):
      self.msg = msg
      self.key = key

   def __str__(self):
      return format_error(self.msg, self.key)

class TokenInsertError(Exception):
   def __init__(self, token, msg=None):
      self.msg = msg
      self.token = token

   def __str__(self):
      return format_error(self.msg, self.token)

class RevokeError(Exception):
   pass
