# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
import io
import json
import urllib2
from collections import OrderedDict
from contextlib import closing

from .. import config
from ..messages import *


def update():
    say("Downloading Can I Use data...")
    try:
        with closing(urllib2.urlopen("https://raw.githubusercontent.com/Fyrd/caniuse/master/fulldata-json/data-2.0.json")) as fh:
            jsonString = fh.read()
    except Exception, e:
        die("Couldn't download the Can I Use data.\n{0}", e)
        return

    try:
        data = json.loads(unicode(jsonString), encoding="utf-8", object_pairs_hook=OrderedDict)
    except Exception, e:
        die("The Can I Use data wasn't valid JSON for some reason. Try downloading again?\n{0}", e)
        return

    # Remove some unused data
    if "cats" in data:
        del data["cats"]
    if "statuses" in data:
        del data["statuses"]

    # Trim agent data to minimum required - mapping codename to full name
    codeNames = {}
    agentData = {}
    for codename,agent in data["agents"].items():
        codeNames[codename] = agent["browser"]
        agentData[agent["browser"]] = codename
    data["agents"] = agentData

    # Trim feature data to minimum - notes and minimum supported version
    def simplifyStatus(s, *rest):
        if "x" in s or "d" in s or "n" in s or "p" in s:
            return "n"
        elif "a" in s:
            return "a"
        elif "y" in s:
            return "y"
        elif "u" in s:
            return "u"
        else:
            die("Unknown CanIUse Status '{0}' for {1}/{2}/{3}. Please report this as a Bikeshed issue.", s, *rest)
            return None
    def simplifyVersion(v):
        if "-" in v:
            # Use the earliest version in a range.
            v,_,_ = v.partition("-")
        return v
    featureData = {}
    for featureName,feature in data["data"].items():
        notes = feature["notes"]
        url = feature["spec"]
        browserData = {}
        for browser,versions in feature["stats"].items():
            descendingVersions = list(reversed(versions.items()))
            mostRecent = descendingVersions[0]
            version = simplifyVersion(mostRecent[0])
            status = simplifyStatus(mostRecent[1], featureName, browser, version)
            if status == "n":
                # Most recent version is broken, so we're done
                pass
            elif status == "u":
                # Seek backwards until I find something other than "u"
                for v,s in descendingVersions:
                    if simplifyStatus(s) != "u":
                        status = simplifyStatus(s)
                        version = simplifyVersion(v)
                        break
            else:
                # Status is either (a)lmost or (y)es,
                # seek backwards thru time as long as it's the same.
                for v,s in descendingVersions:
                    if simplifyStatus(s) == status:
                        version = simplifyVersion(v)
                    else:
                        break
            browserData[codeNames[browser]] = "{0} {1}".format(status, version)
        featureData[featureName] = {"notes":notes, "url":url, "support":browserData}
    data["data"] = featureData

    if not config.dryRun:
        try:
            with closing(io.open(config.scriptPath + "/spec-data/caniuse.json", 'w', encoding="utf-8")) as fh:
                fh.write(unicode(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True)))
        except Exception, e:
            die("Couldn't save Can I Use database to disk.\n{0}", e)
            return
    say("Success!")