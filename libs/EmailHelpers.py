# -*- coding: utf-8 -*-
"""
Created on Apr 12, 2022

@author: bmartin5692

Helper functions for email
"""


def email_rfc2822_compliance(message, max_line_length=900):
    """
    Basic function to make email messages RFC2822 2.1.1 Compliant (Line Length Limit)

    - Split the message at {max_line_length} (default 900)

    Returns:
      - Original message with \\r\\n at max_line_lengths
    """
    returnmsg = ""
    while len(message) > 0:
        returnmsg = returnmsg + message[:max_line_length] + "\r\n"
        message = message[max_line_length:]

    return returnmsg
