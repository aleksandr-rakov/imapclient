"""
Parsing for IMAP command responses with focus on FETCH responses as
returned by imaplib.

Intially inspired by http://effbot.org/zone/simple-iterator-parser.htm
"""

#TODO more exact error reporting

import imaplib
from datetime import datetime
from fixed_offset import FixedOffset
from response_lexer import Lexer


__all__ = ['parse_response', 'ParseError']


class ParseError(ValueError):
    pass


def parse_response(text):
    """Pull apart IMAP command responses.

    Returns nested tuples of appropriately typed objects.
    """
    return tuple(gen_parsed_response(text))


def gen_parsed_response(text):
    if not text:
        return
    src = Lexer.create_token_source(text)
    
    token = None
    try:
        for token in src:
            yield atom(src, token)
    except ParseError:
        raise
    except ValueError, err:
        raise ParseError("%s: %s" % (str(err), token))


def parse_fetch_response(text):
    """Pull apart IMAP FETCH responses as returned by imaplib.

    Returns a dictionary, keyed by message ID. Each value a dictionary
    keyed by FETCH field type (eg."RFC822").
    """
    response = gen_parsed_response(text)

    parsed_response = {}
    while True:
        try:
            msg_id = _int_or_error(response.next(), 'invalid message ID')
        except StopIteration:
            break

        try:
            msg_response = response.next()
        except StopIteration:
            raise ParseError('unexpected EOF')

        if not isinstance(msg_response, tuple):
            raise ParseError('bad response type: %s' % repr(msg_response))
        if len(msg_response) % 2:
            raise ParseError('uneven number of response items: %s' % repr(msg_response))

        # always return the 'sequence' of the message, so it is available
        # even if we return keyed by UID.
        msg_data = {'SEQ': msg_id}
        for i in xrange(0, len(msg_response), 2):
            word = msg_response[i].upper()
            value = msg_response[i+1]

            if word == 'UID':
                msg_id = _int_or_error(value, 'invalid UID')
            elif word == 'INTERNALDATE':
                msg_data[word] = _convert_INTERNALDATE(value)
            else:
                msg_data[word] = value

        parsed_response[msg_id] = msg_data

    return parsed_response


def _int_or_error(value, error_text):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ParseError('%s: %s' % (error_text, repr(value)))


def _convert_INTERNALDATE(date_string):
    mo = imaplib.InternalDate.match('INTERNALDATE "%s"' % date_string)
    if not mo:
        raise ValueError("couldn't parse date %r" % date_string)

    zoneh = int(mo.group('zoneh'))
    zonem = (zoneh * 60) + int(mo.group('zonem'))
    if mo.group('zonen') == '-':
        zonem = -zonem
    tz = FixedOffset(zonem)

    year = int(mo.group('year'))
    mon = imaplib.Mon2num[mo.group('mon')]
    day = int(mo.group('day'))
    hour = int(mo.group('hour'))
    min = int(mo.group('min'))
    sec = int(mo.group('sec'))

    dt = datetime(year, mon, day, hour, min, sec, 0, tz)

    # Normalise to host system's timezone
    return dt.astimezone(FixedOffset.for_system()).replace(tzinfo=None)


def atom(src, token):
    if token == "(":
        out = []
        for token in src:
            if token == ")":
                return tuple(out)
            out.append(atom(src, token))
        # oops - no terminator!
        preceeding = ' '.join(str(val) for val in out)
        raise ParseError('Tuple incomplete before "(%s"' % preceeding)
    elif token == 'NIL':
        return None
    elif token[0] == '{':
        literal_len = int(token[1:-1])
        literal_text = src.current_literal
        if literal_text is None:
           raise ParseError('No literal corresponds to %r' % token)
        if len(literal_text) != literal_len:
            raise ParseError('Expecting literal of size %d, got %d' % (
                                literal_len, len(literal_text)))
        return literal_text
    elif len(token) >= 2 and (token[0] == token[-1] == '"'):
        return token[1:-1]
    elif token.isdigit():
        return int(token)
    else:
        return token
