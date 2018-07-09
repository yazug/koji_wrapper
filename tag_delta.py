#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys

import rpm

from shale.brewtag import BrewTag
from shale import decor
from shale.shalerpm import splitFilename


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--new', action='store_true', default=False,
                        help='show new packages in output')
    parser.add_argument('--delta', action='store_true', default=False,
                        help='show both new and removed packages in output')
    parser.add_argument('-N', '--no-inherit', action='store_true',
                        default=False,
                        help='Do not use inherit when checking tags')
    parser.add_argument('--skip-same', action='store_true', default=False,
                        help='skip printing entries if they are the same')

    parser.add_argument('left_tag', help='left brew tag for comparison')
    parser.add_argument('right_tag', help='right brew tag for comparison')
    args = parser.parse_args()

    show_new = False
    show_removed = False
    do_inherit = True

    if args.new:
        show_new = True
    if args.delta:
        show_new = True
        show_removed = True
    if args.no_inherit:
        do_inherit = False

    upgrades = 0
    downgrades = 0
    rows, columns = os.popen('stty size', 'r').read().split()
    fw = str(int((int(columns)-3)/3))

    ltag = BrewTag(tag=args.left_tag, inherit=do_inherit)
    rtag = BrewTag(tag=args.right_tag, inherit=do_inherit)

    lc = ltag.components()
    rc = rtag.components()
    common = sorted(list(set(lc) & set(rc)))
    new_components = sorted(list(set(rc) - set(lc)))
    old_components = sorted(list(set(lc) - set(rc)))

    print('%d builds in %s' % (len(lc), str(ltag)))
    print('%d builds in %s' % (len(rc), str(rtag)))
    print('Overlap: %d packages (%f %%)' % (len(common),
                                            float(len(common)) /
                                            float(len(lc)) * 100))
    if show_new:
        print('New Packages:', len(new_components))
    if show_removed:
        print('Removed Packages:', len(old_components))

    if sys.stdout.isatty():
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        print(f % ('component', str(ltag), str(rtag)))
        print(f % (decor.line('component'), decor.line(str(ltag)),
                   decor.line(str(rtag))))
    else:
        print()
        print('component,' + str(ltag) + ',' + str(rtag) + ',' + 'status')

    for c in common:
        lnvr = ltag.latest_package(c)
        rnvr = rtag.latest_package(c)
        (ln, lv, lr, le, la) = splitFilename(lnvr)
        (rn, rv, rr, re, ra) = splitFilename(rnvr)

        lvr = lv + '-' + lr
        rvr = rv + '-' + rr
        rebase = False
        v = rpm.labelCompare((le, lv, lr), (re, rv, rr))
        if v < 0 and rv != lv:
            rebase = True

        if sys.stdout.isatty():
            if v > 0:
                f = '%' + fw + 's %s%' + fw + 's %s%' + fw + 's'
                print(f % (c, decor.HILIGHT, lvr, decor.NORMAL, rvr))
                downgrades = downgrades + 1
            elif v < 0:
                f = '%' + fw + 's %' + fw + 's %s%' + fw + 's%s'
                print(f % (c, lvr, decor.HILIGHT, rvr, decor.NORMAL))
                upgrades = upgrades + 1
            elif not args.skip_same:
                f = '%' + fw + 's %' + fw + 's %' + fw + 's'
                print(f % (c, lvr, rvr))
        else:
            if args.skip_same and v == 0:
                continue

            status = ','
            if rebase is True:
                status = ',rebase'
            print(c + ',' + lvr + ',' + rvr + status)

    if show_new:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in new_components:
            rnvr = rtag.latest_package(c)
            (rn, rv, rr, re, ra) = splitFilename(rnvr)
            rvr = rv + '-' + rr
            if sys.stdout.isatty():
                print(f % (c, '---', rvr))
            else:
                print(c + ',---,' + rvr + ',new')

    if show_removed:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in old_components:
            lnvr = ltag.latest_package(c)
            (ln, lv, lr, le, la) = splitFilename(lnvr)
            lvr = lv + '-' + lr
            if sys.stdout.isatty():
                print(f % (c, lvr, '---'))
            else:
                print(c + ',' + lvr + ',---' + ',removed')

    print()
    print('%d builds in %s' % (len(lc), str(ltag)))
    print('%d builds in %s' % (len(rc), str(rtag)))
    print('Overlap: %d packages (%f %%)' % (len(common),
                                            float(len(common)) /
                                            float(len(lc)) * 100))
    print('Downgrades:', downgrades)
    print('Upgrades:', upgrades)
    if show_new:
        print('New Packages:', len(new_components))
    if show_removed:
        print('Removed Packages:', len(old_components))


if __name__ == '__main__':
    main()
