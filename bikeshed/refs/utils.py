# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

from .. import config


def filterObsoletes(refs, replacedSpecs, ignoredSpecs, localShortname=None, localSpec=None):
    # Remove any ignored or obsoleted specs
    possibleSpecs = set(ref.spec for ref in refs)
    if localSpec:
        possibleSpecs.add(localSpec)
    moreIgnores = set()
    for oldSpec, newSpec in replacedSpecs:
        if newSpec in possibleSpecs:
            moreIgnores.add(oldSpec)
    ret = []
    for ref in refs:
        if ref.spec in ignoredSpecs:
            continue
        if ref.spec in moreIgnores:
            continue
        if ref.status != "local" and ref.shortname == localShortname:
            continue
        ret.append(ref)
    return ret


def linkTextVariations(str, linkType):
    # Generate intelligent variations of the provided link text,
    # so explicitly adding an lt attr isn't usually necessary.
    yield str

    if linkType is None:
        return
    elif linkType == "dfn":
        last1 = str[-1] if len(str) >= 1 else None
        last2 = str[-2:] if len(str) >= 2 else None
        last3 = str[-3:] if len(str) >= 3 else None
        # Berries <-> Berry
        if last3 == "ies":
            yield str[:-3] + "y"
        if last1 == "y":
            yield str[:-1] + "ies"

        # Blockified <-> Blockify
        if last3 == "ied":
            yield str[:-3] + "y"
        if last1 == "y":
            yield str[:-1] + "ied"

        # Zeroes <-> Zero
        if last2 == "es":
            yield str[:-2]
        else:
            yield str + "es"

        # Bikeshed's <-> Bikeshed
        if last2 == "'s" or last2 == "’s":
            yield str[:-2]
        else:
            yield str + "'s"

        # Bikesheds <-> Bikeshed
        if last1 == "s":
            yield str[:-1]
        else:
            yield str + "s"

        # Bikesheds <-> Bikesheds'
        if last1 == "'" or last1 == "’":
            yield str[:-1]
        else:
            yield str + "'"

        # Snapped <-> Snap
        if last2 == "ed" and len(str) >= 4 and str[-3] == str[-4]:
            yield str[:-3]
        elif last1 in "bdfgklmnprstvz":
            yield str + last1 + "ed"

        # Zeroed <-> Zero
        if last2 == "ed":
            yield str[:-2]
        else:
            yield str + "ed"

        # Generated <-> Generate
        if last1 == "d":
            yield str[:-1]
        else:
            yield str + "d"

        # Navigating <-> Navigate
        if last3 == "ing":
            yield str[:-3]
            yield str[:-3] + "e"
        elif last1 == "e":
            yield str[:-1] + "ing"
        else:
            yield str + "ing"

        # Snapping <-> Snap
        if last3 == "ing" and len(str) >= 5 and str[-4] == str[-5]:
            yield str[:-4]
        elif last1 in "bdfgklmnprstvz":
            yield str + last1 + "ing"

    elif config.linkTypeIn(linkType, "idl"):
        # Let people refer to escaped IDL names with their "real" names (without the underscore)
        if str[:1] != "_":
            yield "_" + str


def stripLineBreaks(obj):
    it = obj.items() if isinstance(obj, dict) else enumerate(obj)
    for key, val in it:
        if isinstance(val, str):
            obj[key] = unicode(val, encoding="utf-8").rstrip("\n")
        elif isinstance(val, unicode):
            obj[key] = val.rstrip("\n")
        elif isinstance(val, dict) or isinstance(val, list):
            stripLineBreaks(val)
    return obj
