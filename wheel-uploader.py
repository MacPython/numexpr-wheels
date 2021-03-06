#!/usr/bin/env python
""" Download wheels from upstream URL, upload with twine
"""
from __future__ import print_function, absolute_import

import os
from os.path import join as pjoin, splitext, exists, expanduser
import sys
import re
from optparse import OptionParser, Option
if sys.version_info[0] >= 3:
    from urllib.request import urlopen, urlretrieve
else:
    from urllib import urlretrieve
    from urllib2 import urlopen
from subprocess import check_call, PIPE

# From `pip install beautifulsoup4`
from bs4 import BeautifulSoup

__version__ = '0.1'

RACKSPACE_URL='http://wheels.scikit-image.org'

WHEEL_RE = re.compile('^.*\.whl$')

def get_wheel_names(url):
    """ Get wheel names from HTML directory listing
    """
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    # This is almost certainly specific to the Rackspace directory
    cells = soup.findAll('td', attrs='colname', text=WHEEL_RE)
    if cells:
        return [cell.text for cell in cells]
    # Works for e.g. Apache directory listing, looking in contents of links
    cells = soup.findAll('a', text=WHEEL_RE)
    if cells:
        return [cell.text for cell in cells]
    cells = soup.findAll(text=WHEEL_RE)
    return [str(cell) for cell in cells]


def main():
    parser = OptionParser(
        usage="%s PACKAGE_NAME VERSION\n\n" % sys.argv[0] + __doc__,
        version="%prog " + __version__)
    parser.add_option(
        Option("-u", "--wheel-url-dir", type='string', default=RACKSPACE_URL,
               help="URL for web directory containing wheels for uploading "
               "[default %default]"))
    parser.add_option(
        Option("-w", "--wheel-dir",
               action="store", type='string', default=os.getcwd(),
               help="Directory to store downloaded wheels [defaults to "
               "current working directory]"))
    parser.add_option(
        Option("-t", "--wheel-type",
               action="store", type='string', default="macosx",
               help="Platform type of wheels to download "
               "[default %default], one of 'all', 'macosx', 'win', "
               "'manylinux1', 'linux'"))
    parser.add_option(
        Option("-c", "--clobber",
               action="store_true",
               help="Overwrite pre-existing wheels"))
    parser.add_option(
        Option("-n", "--no-twine",
               action="store_true",
               help="Do not upload wheels with twine"))
    parser.add_option(
        Option("-s", "--sign",
               action="store_true",
               help="Sign wheels before upload"))
    parser.add_option(
        Option("-r", "--repository",
               help="Repository to upload to [defaults to pypi]"))
    parser.add_option(
        Option("-v", "--verbose",
               action="store_true",
               help="Give more feedback"))
    (opts, pkg_identifiers) = parser.parse_args()
    wheel_dir = expanduser(opts.wheel_dir)
    wheel_url_dir = opts.wheel_url_dir
    if not wheel_url_dir.endswith('/'):
        wheel_url_dir += '/'
    if len(pkg_identifiers) != 2:
        parser.print_help()
        sys.exit(1)
    pkg_name, pkg_version = pkg_identifiers
    wheel_root = '{0}-{1}-'.format(pkg_name, pkg_version)
    try:
        check_call(['twine', '-h'], stdout=PIPE)
    except OSError:
        raise RuntimeError('Please install "twine" utility')
    twine_opts = ['--sign'] if opts.sign else []
    if opts.repository:
        twine_opts += ['--repository=' + opts.repository]
    wheel_names = get_wheel_names(wheel_url_dir)
    copied_wheels = []
    found_wheels = []
    for wheel_name in wheel_names:
        if not wheel_name.startswith(wheel_root):
            continue
        root, ext = splitext(wheel_name)
        project, version, pyv, pycv, plat = root.split('-')
        if opts.wheel_type != 'all' and not opts.wheel_type in plat:
            continue
        wheel_url = wheel_url_dir + wheel_name
        wheel_path = pjoin(wheel_dir, wheel_name)
        found_wheels.append(wheel_path)
        if exists(wheel_path) and not opts.clobber:
            if opts.verbose:
                print('Not overwriting {0}'.format(wheel_path))
            continue
        if opts.verbose:
            print("Downloading {0} to {1}".format(wheel_url, wheel_path))
        urlretrieve(wheel_url, wheel_path)
        copied_wheels.append(wheel_path)
    if len (found_wheels) == 0:
        raise RuntimeError('Found no wheels at {0} for {1} and type {2}'.format(
            opts.wheel_url_dir, wheel_root, opts.wheel_type))
    if opts.no_twine:
        if opts.verbose:
            print("Found wheels but not uploading because of "
                    "--no-twine flag\n{0}".format(
                    '\n'.join(found_wheels)))
        return
    check_call(['twine', 'upload'] + twine_opts + found_wheels)


if __name__ == '__main__':
    main()
