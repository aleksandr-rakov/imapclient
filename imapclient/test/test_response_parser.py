# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright 2009 Menno Smits

'''
Unit tests for the FetchTokeniser and FetchParser classes
'''

import unittest
from imapclient.response_parser import parse_response
from imapclient.fixed_offset import FixedOffset
from pprint import pformat

#TODO: tokenising tests
#TODO: test invalid dates and times
#TODO: more response types
#TODO: clean up this file

system_offset = FixedOffset.for_system()
def datetime_to_native(dt):
    return dt.astimezone(system_offset).replace(tzinfo=None)


class TestParseResponse(unittest.TestCase):

    def test_string(self):
        self._test('"TEST"', 'TEST')

    def test_int(self):
        self._test('45', 45)

    def test_nil(self):
        self._test('NIL', None)

    def test_empty_tuple(self):
        self._test('()', ())

    def test_tuple(self):
        self._test('(123 "foo")', (123, 'foo'))

    def test_int_and_tuple(self):
        self._test('1 (123 "foo")', (1, (123, 'foo')), wrap=False)

    def test_nested_tuple(self):
        self._test('(123 "foo" ("more" NIL) 66)',
                   (123, "foo", ("more", None), 66))

    def test_deeper_nest_tuple(self):
        self._test('(123 "foo" ((0 1 2) "more" NIL) 66)',
                   (123, "foo", ((0, 1, 2), "more", None), 66))

    def test_complex_mixed(self):
        self._test('(("TEXT" "PLAIN" ("CHARSET" "US-ASCII") NIL NIL "7BIT" 1152 23)'
                   '("TEXT" "PLAIN" ("CHARSET" "US-ASCII" "NAME" "cc.diff") '
                   '"<hi.there>" "foo" "BASE64" 4554 73) "MIXED")',
                   (('TEXT', 'PLAIN', ('CHARSET', 'US-ASCII'), None, None, '7BIT', 1152, 23),
                    ('TEXT', 'PLAIN', ('CHARSET', 'US-ASCII', 'NAME', 'cc.diff'),
                    '<hi.there>', 'foo', 'BASE64', 4554, 73), 'MIXED'))

    def _test(self, to_parse, expected, wrap=True):
        # convenience - expected value should be wrapped in another tuple
        if wrap:
            expected = (expected,)
        output = parse_response(to_parse)
        self.assert_(
                output == expected,
                format_error(to_parse, output, expected),
            )
#     def testCharacterCase(self):
#         '''Test handling of varied case in the response type name
#         '''
#         self._parse_test(
#             [r'2 (flaGS (\Deleted Foo \Seen))'],
#             {2: {'FLAGS': [r'\Deleted', 'Foo', r'\Seen']}}
#             )

#     def testGarbage(self):
#         self.assertRaises(ValueError, self.p, [r'2 (FLAGS (\Deleted) MORE)'])


#     def test_INTERNALDATE(self):

#         def check(date_str, expected_dt):
#             output = self.p(['3 (INTERNALDATE "%s")' % date_str])
#             assert output.keys() == [3]
#             assert output[3].keys() == ['INTERNALDATE']
#             actual_dt = output[3]['INTERNALDATE']

#             # Returned date should be in local timezone
#             self.assert_(actual_dt.tzinfo is None)

#             expected_dt = datetime_to_native(expected_dt)
#             self.assert_(actual_dt == expected_dt,
#                          '%s != %s' % (actual_dt, expected_dt))

#         dt = check(' 9-Feb-2007 17:08:08 -0430',
#                    datetime.datetime(2007, 2, 9, 17, 8, 8, 0, FixedOffset(-4*60 - 30)))
 
#         dt = check('12-Feb-2007 17:08:08 +0200',
#                    datetime.datetime(2007, 2, 12, 17, 8, 8, 0, FixedOffset(2*60)))
 
#         dt = check(' 9-Dec-2007 17:08:08 +0000',
#                    datetime.datetime(2007, 12, 9, 17, 8, 8, 0, FixedOffset(0)))


#     def testMultipleTypes(self):
#         '''Test multiple response types'''
#         self._parse_test(
#             [r'2 (FLAGS (\Deleted Foo \Seen) INTERNALDATE " 9-Feb-2007 17:08:08 +0000")'],
#             {2: {
#                     'FLAGS': [r'\Deleted', 'Foo', r'\Seen'],
#                     'INTERNALDATE': datetime_to_native(datetime.datetime(2007, 2, 9,
#                                                                          17, 8, 8, 0,
#                                                                          FixedOffset(0)))
#                     }
#                 }
#             )

#     def testMultipleMessages(self):
#         '''Test with multple messages in the response
#         '''
#         self._parse_test(
#             [
#                 r'2 (FLAGS (Foo Bar))',
#                 r'7 (FLAGS (Baz Sneeve))',
#                 ],
#             {
#                 2: {'FLAGS': ['Foo', 'Bar']},
#                 7: {'FLAGS': ['Baz', 'Sneeve']},
#                 }
#             )

#     def testLiteral(self):
#         '''Test literal handling
#         '''
#         self._parse_test(
#             [('1 (RFC822 {21}', 'Subject: test\r\n\r\nbody'), ')'],
#             { 1: {'RFC822': 'Subject: test\r\n\r\nbody'} }
#             )

#     def testMultipleLiterals(self):
#         self._parse_test(
#             [
#                 ('1 (RFC822.TEXT {4}', 'body'),
#                 (' RFC822 {21}', 'Subject: test\r\n\r\nbody'),
#                 ')'
#                 ],
#             { 1: {
#                     'RFC822.TEXT': 'body',
#                     'RFC822': 'Subject: test\r\n\r\nbody',
#                     }
#                 }
#             )

#     def testMultiTypesWithLiteral(self):
#         self._parse_test(
#             [
#                 ('1 (INTERNALDATE " 9-Feb-2007 17:08:08 +0100" RFC822 {21}',
#                       'Subject: test\r\n\r\nbody'),
#                 ')'
#                 ],
#             {1: {
#                     'INTERNALDATE': datetime_to_native(datetime.datetime(2007, 2, 9,
#                                                                          17, 8, 8, 0,
#                                                                          FixedOffset(60))),
#                     'RFC822': 'Subject: test\r\n\r\nbody',
#                     }
#                 }
#             )

#     def testLiteralsWithSections(self):
#         self._parse_test(
#             [('1 (BODY[TEXT] {11}', 'Hi there.\r\n'), ')'],
#             { 1: {'BODY[TEXT]': 'Hi there.\r\n',} }
#             )

#     def testLiteralsWithSectionsAndOtherParts(self):
#         self._parse_test(
#             [('1 (FLAGS (\\Seen) UID 2 BODY[HEADER.FIELDS (FROM)] {21}',
#               'From: foo@foo.com\r\n'), ')'],
#             {2: { 'BODY[HEADER.FIELDS (FROM)]': 'From: foo@foo.com\r\n',
#                   'FLAGS': ['\\Seen'],
#                    }
#                 }
#             )

#     def testUID(self):
#         '''Test UID handling. The UID is returned instead of the given message
#         ID if present.
#         '''
#         self._parse_test(
#             ['1 (UID 8)'],
#             {8: {}}
#             )


def format_error(input_, output, expected):
    return 'failed for:\n%s\ngot:\n%s\nexpected:\n%s' % (
                pformat(input_),
                pformat(output),
                pformat(expected),
            )

# class TestFetchTokeniser(unittest.TestCase):
#     def setUp(self):
#         self.t = FetchTokeniser()

#     def testEmptyList(self):
#         self._test_list('', [])

#     def testOneItemList(self):
#         self._test_list('123', [123])

#     def testWordsInList(self):
#         self._test_list('test stuff', ['test', 'stuff'])

#     def testQuotedStringInList(self):
#         self._test_list('"test stuff" and more', ['test stuff', 'and', 'more'])

#     def testNILInList(self):
#         self._test_list('test NIL stuff', ['test', None, 'stuff'])

#     def testEmptyListPair(self):
#         self._test_pairs('FOO ()', [('FOO', [])])

#     def testIntPair(self):
#         self._test_pairs('FOO 123', [('FOO', 123)])

#     def testQuotedStringPair(self):
#         self._test_pairs('FOO "abc def"', [('FOO', "abc def")])

#     def testComplexListPair(self):
#         self._test_pairs('FOO (123 "a b c" \\XYZ)', [('FOO', [123, "a b c", '\\XYZ'])])

#     def testMultiplePairs(self):
#         self._test_pairs('FOO 123 bar (def "XYZ") MORE "stuff"', [
#             ('FOO', 123),
#             ('bar', ['def', 'XYZ']),
#             ('MORE', 'stuff'),
#             ])

#     def testNoPairs(self):
#         self._test_pairs('', [])

#     def testGarbage(self):
#         self.assertRaises(ValueError,
#                 self.t.process_pairs, 'FOO 123 BAH "abc" WHAT?')
#         self.assertRaises(ValueError,
#                 self.t.process_pairs, 'HMMM FOO 123 BAH "abc"')
#         self.assertRaises(ValueError,
#                 self.t.process_pairs, 'FOO 123 BAD BAH "abc"')

#     def testLiteral(self):
#         self._test_pairs('FOO {21}', [('FOO', Literal(21))])

#     def _test_pairs(self, input_, expected):
#         output = self.t.process_pairs(input_)
#         self.assert_(
#                 output == expected,
#                 format_error(input_, output, expected),
#             )
#         return output

#     def _test_list(self, input_, expected):
#         output = self.t.process_list(input_)
#         self.assert_(
#                 output == expected,
#                 format_error(input_, output, expected),
#             )
#         return output

# example1 = '("TEXT" "PLAIN" ("CHARSET" "US-ASCII") NIL NIL "7BIT" 2279 48)'
# example2 = '(("TEXT" "PLAIN" ("CHARSET" "US-ASCII") NIL NIL "7BIT" 1152 23)("TEXT" "PLAIN" ("CHARSET" "US-ASCII" "NAME" "cc.diff") "<960723163407.20117h@cac.washington.edu>" "Compiler diff" "BASE64" 4554 73) "MIXED")'
# example3 = '1 FETCH (UID 1 INTERNALDATE "18-Oct-2009 19:59:06 +0100")'
# err1 = '1 FETCH (UID '

# print parse_response(example1)
# print parse_response(example2)
# print parse_response(example3)
# print parse_response(err1)

if __name__ == '__main__':
    unittest.main()
