#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Written by Martin v. L�wis <loewis@informatik.hu-berlin.de>
#
# Changelog: (Guilherme Polo)
#   2009-03-08
#    - main accepts a custom argv now.
#    - Added -v, -c, -s as noop.
#
#   2008-04-11
#    - Support for files with BOM UTF8 mark.
#
#   2008-04-10
#    - Support for fuzzy strings in output.
#    - Bumped to version 1.1.1
#
#
# License for code in this file that was taken from Python 2.5.
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF
# hereby grants Licensee a nonexclusive, royalty-free, world-wide
# license to reproduce, analyze, test, perform and/or display publicly,
# prepare derivative works, distribute, and otherwise use Python
# alone or in any derivative version, provided, however, that PSF's
# License Agreement and PSF's notice of copyright, i.e., "Copyright (c)
# 2001, 2002, 2003, 2004, 2005, 2006, 2007 Python Software Foundation;
# All Rights Reserved" are retained in Python alone or in any derivative
# version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.



"""Generate binary message catalog from textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This is essentially the same function as the
GNU msgfmt program, however, it is a simpler implementation.

Usage: msgfmt.py [OPTIONS] filename.po

Options:
    -o file
    --output-file=file
        Specify the output file to write to.  If omitted, output will go to a
        file named filename.mo (based off the input file name).

    -f
    --use-fuzzy
        Use fuzzy entries in output

    -h
    --help
        Print this message and exit.

    -V
    --version
        Display version information and exit.

    -v
    --verbose
        No op. Added for making it easier to use this as a fallback for
        GNU msgfmt.

    -c
    --check
        No op. Added for making it easier to use this as a fallback for
        GNU msgfmt.

    -s
    --statistics
        No op. Added for making it easier to use this as a fallback for
        GNU msgfmt.


Before using the -f (fuzzy) option, read this:
    http://www.finesheer.com:8457/cgi-bin/info2html?(gettext)Fuzzy%20Entries&lang=en
"""

import sys
import os
import getopt
import struct
import array
import codecs

__version__ = "1.1.1"

MESSAGES = {}


def usage(code, msg=''):
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)


def add(id, str, fuzzy, use_fuzzy):
    "Add a translation to the dictionary."
    global MESSAGES
    if (not fuzzy or use_fuzzy) and str:
        MESSAGES[id] = str


def generate():
    "Return the generated output."
    global MESSAGES
    keys = MESSAGES.keys()
    # the keys are sorted in the .mo file
    keys.sort()
    offsets = []
    ids = strs = ''
    for id in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(ids), len(id), len(strs), len(MESSAGES[id])))
        ids += id + '\0'
        strs += MESSAGES[id] + '\0'
    output = ''
    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # and the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412deL,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size and offset of hash table
    output += array.array("i", offsets).tostring()
    output += ids
    output += strs
    return output


def make(filename, outfile, use_fuzzy):
    ID = 1
    STR = 2

    # Compute .mo name from .po name and arguments
    if filename.endswith('.po'):
        infile = filename
    else:
        infile = filename + '.po'
    if outfile is None:
        outfile = os.path.splitext(infile)[0] + '.mo'

    try:
        lines = open(infile).readlines()
        if lines[0].startswith(codecs.BOM_UTF8):
            lines[0] = lines[0][len(codecs.BOM_UTF8):]
    except IOError, msg:
        print >> sys.stderr, msg
        sys.exit(1)

    section = None
    fuzzy = 0

    # Parse the catalog
    lno = 0
    for l in lines:
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if l[0] == '#' and section == STR:
            add(msgid, msgstr, fuzzy, use_fuzzy)
            section = None
            fuzzy = 0
        # Record a fuzzy mark
        if l[:2] == '#,' and 'fuzzy' in l:
            fuzzy = 1
        # Skip comments
        if l[0] == '#':
            continue
        # Now we are in a msgid section, output previous section
        if l.startswith('msgid'):
            if section == STR:
                add(msgid, msgstr, fuzzy, use_fuzzy)
            section = ID
            l = l[5:]
            msgid = msgstr = ''
        # Now we are in a msgstr section
        elif l.startswith('msgstr'):
            section = STR
            l = l[6:]
        # Skip empty lines
        l = l.strip()
        if not l:
            continue
        # XXX: Does this always follow Python escape semantics?
        l = eval(l)
        if section == ID:
            msgid += l
        elif section == STR:
            msgstr += l
        else:
            print >> sys.stderr, 'Syntax error on %s:%d' % (infile, lno), \
                  'before:'
            print >> sys.stderr, l
            sys.exit(1)
    # Add last entry
    if section == STR:
        add(msgid, msgstr, fuzzy, use_fuzzy)

    # Compute output
    output = generate()

    try:
        open(outfile,"wb").write(output)
    except IOError,msg:
        print >> sys.stderr, msg


def main(argv=sys.argv[1:]):
    try:
        opts, args = getopt.getopt(argv, 'hVo:fvcs', [
            'help', 'version', 'output-file=', 'use-fuzzy',
            # no op
            'verbose', 'check', 'statistics'])
    except getopt.error, msg:
        usage(1, msg)

    outfile = None
    use_fuzzy = False
    # parse options
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-V', '--version'):
            print >> sys.stderr, "msgfmt.py", __version__
            sys.exit(0)
        elif opt in ('-f', '--use-fuzzy'):
            use_fuzzy = True
        elif opt in ('-o', '--output-file'):
            outfile = arg
    # do it
    if not args:
        print >> sys.stderr, 'No input file given'
        print >> sys.stderr, "Try `msgfmt --help' for more information."
        return

    for filename in args:
        make(filename, outfile, use_fuzzy)


if __name__ == '__main__':
    main()
