#!/usr/bin/env python
import sys
import re
import graypy
import logging
import argparse

# Copyright (c) 2012 Anton Tolchanov <me@knyar.net>
# https://github.com/knyar/apache2gelf

parser = argparse.ArgumentParser(description='Reads apache error log on stdin and delivers messages to graylog2 server via GELF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Add the following to apache virtualhost configuration to use:\n" +
        'ErrorLog "||/path/to/errorlog2gelf.py')
parser.add_argument('--host', dest='host', default='localhost', help='graylog2 server hostname (default: localhost)')
parser.add_argument('--port', dest='port', default='12201', help='graylog2 server port (default: 12201)')
parser.add_argument('--facility', dest='facility', default='access_log', help='logging facility (default: access_log)')
parser.add_argument('--vhost', dest='vhost', help='Add additional "vhost" field to all log records. This can be used to differentiate between virtual hosts.')
args = parser.parse_args()

regexp = '^\[[^]]*\] \[([^]]*)\] \[client (?P<ipaddr>[0-9\.]+)\] (.*)'

baserecord = {}
if args.vhost: baserecord['vhost'] = args.vhost

logger = logging.getLogger(args.facility)
logger.setLevel(logging.DEBUG)
logger.addHandler(graypy.GELFHandler(args.host, int(args.port), debugging_fields=False))

for line in iter(sys.stdin.readline, b''):
    print line.rstrip()

    matches = re.search(regexp, line)
    if matches:
        record = baserecord
        record.update(matches.groupdict())
	adapter = logging.LoggerAdapter(logging.getLogger(args.facility), record)
        if args.vhost:
            adapter.error('%s %s %s: %s' % (matches.group(2), args.vhost, matches.group(1), matches.group(3)))
        else:
            adapter.error('%s %s: %s' % (matches.group(2), matches.group(1), matches.group(3)))

