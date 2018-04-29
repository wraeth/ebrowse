#!/usr/bin/env python3

"""Builds a list of installed packages"""

import curses
import curses.panel
import logging
import textwrap
from math import ceil

from ebrowse import packages

log = logging.getLogger('ebrowse.ncurses')


def draw_pkglist(box, pos: int, page: int, pkglist: list) -> None:
    """
    Draw the package list.

    :param box: the stdscr.box() object in which to draw
    :param pos: current cursor position
    :param page: current page
    :param pkglist: list of package cpv's
    :return: None
    """
    log.debug('Drawing pkglist window: pos %d, pg %d' % (pos, page))
    length = curses.LINES - 3
    pages = int(ceil(len(pkglist) / length))

    box.erase()
    box.box()

    for line in range(1 + (length * (page - 1)), length + 1 + (length * (page - 1))):
        if len(pkglist) == 0:
            box.addstr(1, 1, 'No installed packages!', curses.A_REVERSE)
        else:
            try:
                if line + (length * (page - 1)) == pos + (length * (page - 1)):
                    box.addstr(line - (length * (page - 1)), 2, pkglist[line - 1], curses.A_REVERSE)
                else:
                    box.addstr(line - (length * (page - 1)), 2, pkglist[line - 1], curses.A_NORMAL)
                if line == length:
                    break
            except IndexError:
                # It's the end of the road as we know it
                break

    # bottom pkgcount/pagecount
    box.addstr(length + 1, 6, 'Pkg %d / %d - Pg %d / %d' % (pos, len(pkglist), page, pages), curses.A_BOLD)


def draw_detail(box, cpv: str) -> None:
    """
    Draw details page on right of screen.

    :param box: window on which to draw
    :param cpv: str(cpv) to detail
    :return: None
    """
    # Package = namedtuple('Package', ['cpv', 'bdep', 'rdep', 'iuse', 'desc', 'home'])
    log.debug('drawing detail for %r' % cpv)
    package = packages.package_detail(cpv)

    # TODO: This needs to be a pad - draw the whole lot, move the viewport.
    #       At present, it stops adding a line beyond the draw screen, but falls over where a line character-wraps to
    #       a line below the draw (eg use-depend strings with python_targets_* and the like).
    #       I guess this would also necessitate a scroll_detail() that doesn't erase the window first.

    # TODO: better parsing/splitting of *DEPEND vars
    #       At present it's a simple word-wrap that doesn't consider groupings (eg "|| ( dep1 dep2 )". This needs to
    #       better handle grouping such that:
    #
    #           dep1
    #           dep2
    #           flag1? ( dep3 dep4 )
    #           flag2? ( || (
    #               dep5
    #               dep6
    #           ) )
    #
    #       This'll be made even more complex with nested conditionals :)

    box.erase()
    box.box()

    max_x, max_y = box.getmaxyx()
    max_x -= 1
    line = 1  # starting line
    align_width = 15

    box.addstr(line, 2, 'Package CPV: %s' % package.cpv, curses.A_BOLD)
    line += 2
    if line == max_x:
        return

    box.addstr(line, 2, 'Description:', curses.A_BOLD)
    for descline in textwrap.wrap(package.desc, max_y - (align_width + 1)):
        box.addstr(line, align_width, descline)
        line += 1
        if line == max_x:
            return

    box.addstr(line, 2, 'Homepage   :', curses.A_BOLD)
    box.addstr(line, align_width, package.home)
    line += 2
    if line == max_x:
        return

    box.addstr(line, 2, 'DEPEND:', curses.A_BOLD)
    if package.bdep is not None and package.bdep is not '':
        for dep in package.bdep.split():
            box.addstr(line, align_width, dep)
            line += 1
            if line == max_x:
                return

    line += 1
    if line == max_x:
        return
    box.addstr(line, 2, 'RDEPEND', curses.A_BOLD)
    if package.rdep is not None and package.rdep is not '':
        for dep in package.rdep.split():
            box.addstr(line, align_width, dep)
            line += 1
            if line == max_x:
                return

    line += 1
    if line == max_x:
        return
    box.addstr(line, 2, 'IUSE:', curses.A_BOLD)
    if package.iuse is not None and package.iuse is not '':
        for useline in textwrap.wrap(package.iuse, max_y - (align_width + 1)):
            box.addstr(line, align_width, useline)
            line += 1
            if line == max_x:
                return


def key_down(pos: int, page: int, page_len: int, pages: int, total_pkgs: int):
    """
    Handler for key-down action.

    :param pos: Current cursor position
    :param page: Current page
    :param page_len: Number of packages listed on a page
    :param pages: Total number of pages
    :param total_pkgs: Total number of packages
    :return: int(position), int(page)
    """
    if page == 1:
        if pos < page_len:
            pos = pos + 1
        else:
            if pages > 1:
                page = page + 1
                pos = 1 + (page_len * (page - 1))
    elif page == pages:
        if pos < total_pkgs:
            pos = pos + 1
    else:
        if pos < page_len + (page_len * (page - 1)):
            pos = pos + 1
        else:
            page = page + 1
            pos = 1 + (page_len * (page - 1))

    log.debug('new pos: %d, page %d' % (pos, page))

    return pos, page


def key_up(pos: int, page: int, page_len: int, pages: int, total_pkgs: int):
    """
    Handler for key-up action.

    :param pos: Current cursor position
    :param page: Current page
    :param page_len: Number of packages listed on a page
    :param pages: Total number of pages
    :param total_pkgs: Total number of packages
    :return: int(position), int(page)
    """
    if page == 1:
        if pos > 1:
            pos = pos - 1
    else:
        if pos > (1 + (page_len * (page - 1))):
            pos = pos - 1
        else:
            page = page - 1
            pos = page_len + (page_len * (page - 1))

    log.debug('new pos: %d, page %d' % (pos, page))

    return pos, page


def key_right(pos: int, page: int, page_len: int, pages: int, total_pkgs: int):
    """
    Scroll the package list further one page.

    :param pos: Current cursor position
    :param page: Current page
    :param page_len: Number of packages listed on a page
    :param pages: Total number of pages
    :param total_pkgs: Total number of packages
    :return: int(position), int(page)
    """
    if page == pages:
        pass
    else:
        if total_pkgs < page_len + (page_len * (page + 1)):
            page += 1
            pos = total_pkgs
        else:
            page += 1
            pos += page_len

    return pos, page


def key_left(pos: int, page: int, page_len: int, pages: int, total_pkgs: int):
    """
    Scroll the package list back one page.

    :param pos: Current cursor position
    :param page: Current page
    :param page_len: Number of packages listed on a page
    :param pages: Total number of pages
    :param total_pkgs: Total number of packages
    :return: int(position), int(page)
    """
    if page == 1:
        pass
    else:
        page -= 1
        pos -= page_len

    return pos, page


def make_panel(width, lines, pos_y=0, pos_x=0):
    """
    Create a new panel on which to draw. Note that the panel will have a border, so effective surface area will in fact
    be 1x1 - width-1 x height-1.

    :param width: total width of the panel.
    :param lines:
    :param pos_y:
    :param pos_x:
    :return:
    """
    log.debug('making new panel: %dx%d origin %dx%d' % (width, lines, pos_x, pos_y))
    this_win = curses.newwin(width, lines, pos_y, pos_x)
    this_win.erase()
    this_win.box()
    return this_win, curses.panel.new_panel(this_win)


def init_interface(stdscr):
    """
    Initialise the interface.

    :return: None
    """
    log.info('setting up curses interface')

    try:
        curses.curs_set(0)
    except AttributeError:
        pass

    installed_package_list = packages.get_installed_packages()
    cpv_list = list(installed_package_list.keys())
    cpv_list.sort()
    cpv_count = len(cpv_list)

    # get widest cpv so we can appropriately size the box
    cpv_len = 0
    for cpv in installed_package_list.keys():
        if len(cpv) > cpv_len:
            cpv_len = len(cpv)

    # i is grate artiste
    log.debug("curses says we're %d cols and %d lines big" % (curses.COLS, curses.LINES))
    win_pkglist, pnl_pkglist = make_panel(curses.LINES, cpv_len + 4)
    win_detail, pnl_detail = make_panel(curses.LINES, curses.COLS - ((cpv_len + 4) - 1), 0, (cpv_len + 4) - 1)

    page_len = curses.LINES - 3
    pages = int(ceil(cpv_count / page_len))

    cursor_pos = 1
    current_page = 1

    draw_pkglist(win_pkglist, cursor_pos, current_page, cpv_list)
    draw_detail(win_detail, cpv_list[cursor_pos - 1])
    curses.panel.update_panels()
    stdscr.refresh()

    key_actions = {
        curses.KEY_UP: 'key_up',
        curses.KEY_DOWN: 'key_down',
        curses.KEY_RIGHT: 'key_right',
        curses.KEY_LEFT: 'key_left'
    }

    # main loop
    log.debug('entering curses loop')
    keycode = stdscr.getch()
    while keycode != 27:
        if keycode == ord('q') or keycode == ord('Q'):
            log.info('user quit')
            break

        try:
            action = key_actions[keycode]
            cursor_pos, current_page = globals()[action](cursor_pos, current_page, page_len, pages, cpv_count)
        except KeyError:
            # just don't do it, i guess
            pass

        # keys to implement (these need pkgdetail to be a pad)
        # curses.KEY_PPAGE - scroll detail up
        # curses.KEY_NPAGE - scroll detail down

        draw_pkglist(win_pkglist, cursor_pos, current_page, cpv_list)
        draw_detail(win_detail, cpv_list[cursor_pos - 1])
        curses.panel.update_panels()
        stdscr.refresh()

        keycode = stdscr.getch()


def main() -> int:
    """
    Entry point into curses interface.

    :return: int(return_code)
    """
    try:
        curses.wrapper(init_interface)
    except Exception as err:
        log.exception(err)
        raise
    return 0
