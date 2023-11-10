# -*- coding: utf-8 -*-
"""
Created on Apr 12, 2022
Updated on Nov 10, 2023
@author: bmartin5692

Helper functions for email
"""
import logging
import smtplib
from email.message import EmailMessage
from email.header import Header
from email.utils import formataddr
from base64 import encodebytes as _bencode
from tornado.options import options

def send_email_message(to_addrs, message):
  """Try to send email message

  Args:      
      to_addrs (list[str]): addresses to send message to
      message (EmailMessage): EmailMessage to send
  """
  try:
      if options.mail_port == 465:
          smtpObj = smtplib.SMTP_SSL(
              options.mail_host, port=options.mail_port, timeout=5
          )
      else:
          smtpObj = smtplib.SMTP(
              options.mail_host, port=options.mail_port, timeout=5
          )
          smtpObj.starttls()
  except Exception as e:
      logging.warning("SMTP Failed with Connection issue (%s)." % e)
      return
  smtpObj.set_debuglevel(False)
  try:
      try:
          smtpObj.login(options.mail_username, options.mail_password)
      except smtplib.SMTPNotSupportedError as e:
          logging.warning(
              "SMTP Auth issue (%s). Attempting to send anyway." % e
          )
      smtpObj.send_message(message, from_addr=options.mail_sender, to_addrs=to_addrs)                
  finally:
      smtpObj.quit()

def create_email_headers(user, subject):
  """Create headers for an EmailMessage
    - From, To, Subject convert unicode properly

  Args:
      user (User): user to email
      subject (str): becomes {game_name} {subject}

  Returns:
      dict: Dictionary of headers
  """
  header = {}  
  header['From'] = formataddr((str(options.game_name), str(options.mail_sender)))  
  header['To'] = formataddr((str(user.name), str(user.email)))
  header['Subject'] = str(Header(str("%s %s" % (options.game_name, subject))))
  return header
  
def get_email_message(headers: dict, body: EmailMessage):
  """Get/Create email message to send

  Args:
      headers (dict): headers to add to the message
      body (EmailMessage): the body for a new message or an EmailMessage to use

  Returns:
      EmailMessage: the message to send
  """
  if not isinstance(body, EmailMessage):    
    # create a new message if body isnt one
    message = EmailMessage()
    message.set_content(body) 
    message.set_type("text/html")
  else:
    message = body
    
  for header, value in headers.items():
    # add headers to message
    message.add_header(header, value)
  
  try:
    # we try to base64 encode
    orig = message.get_payload(decode=True)
    encdata = str(_bencode(orig), 'ascii')
    message.set_payload(encdata)
    message.replace_header('Content-Transfer-Encoding', 'base64')        
  except:
    # if encoding fails it will send as plain text
    pass
  
  return message

