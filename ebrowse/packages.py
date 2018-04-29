#!/usr/bin/env python3

"""Portage interface to package browser."""

import logging

import portage

from collections import namedtuple

Package = namedtuple('Package', ['cpv', 'bdep', 'rdep', 'iuse', 'desc', 'home'])
port = portage.db[portage.root]['vartree']

log = logging.getLogger('ebrowse.packages')

__all__ = [
    'get_installed_packages',
    'package_detail',
    'Package'
]


def get_installed_packages() -> dict:
    """Iterate cpv_all to build {cpv: Package()}"""
    log.debug('Getting installed CPV list using portage root %r' % portage.root)
    installed_cpv = port.dbapi.cpv_all()

    packages = {}
    maxcpvlen = 0

    # get attributes
    for cpv in installed_cpv:
        packages[cpv] = Package(cpv, *port.dbapi.aux_get(cpv, ['DEPEND', 'RDEPEND', 'IUSE', 'DESCRIPTION', 'HOMEPAGE']))
        if len(cpv) > maxcpvlen:
            maxcpvlen = len(cpv)
    log.info('got %d installed CPVs' % len(packages.keys()))

    return packages


def package_detail(cpv: str) -> Package:
    """
    Interrogate portage for details of the specified CPV.

    :param cpv: fully qualified category/package-version
    :return: Package(cpv, bdep, rdep, iuse, desc, homepage)
    """
    log.debug('Getting package info for %r' % cpv)
    return Package(cpv, *port.dbapi.aux_get(cpv, ['DEPEND', 'RDEPEND', 'IUSE', 'DESCRIPTION', 'HOMEPAGE']))
