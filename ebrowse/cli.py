#!/usr/bin/env python3

"""Main entry point into program."""

import argparse
import logging


def main() -> int:
    """
    Entry point into the utility.

    :return: int
    """
    parser = argparse.ArgumentParser(description='Utility for browsing portage package list')
    parser.add_argument('-v', '--version', help='Print version information', action='store_true')
    parser.add_argument('-l', '--logfile', help='Log destination')
    parser.add_argument('-d', '--debug', help='Enable debug logging', action='store_true')

    mode_parser = parser.add_mutually_exclusive_group()
    mode_parser.add_argument('-n', '--ncurses', help='Use the ncurses interface (default)', action='store_true', default=True)

    args = parser.parse_args()

    import ebrowse
    if args.version:
        print('%s v%s' % (ebrowse.__NAME__, ebrowse.__VERSION__))
        return 0

    # initialise logging
    if not args.logfile:
        logging.basicConfig(handlers=[logging.NullHandler()])
    else:
        log_level = logging.INFO
        if args.debug:
            log_level = logging.DEBUG
        logging.basicConfig(level=log_level, filename=args.logfile)

    log = logging.getLogger('ebrowse')
    log.info('%s v%s' % (ebrowse.__NAME__, ebrowse.__VERSION__))
    log.debug('Started with arguments: %s' % args._get_kwargs())

    if args.ncurses:
        import ebrowse.ncurses
        return ebrowse.ncurses.main()


if __name__ == '__main__':
    main()
