#!/usr/bin/env python
# coding: utf-8

"""
Using the navigation timings api, see descriptions at the bottom.
pip install selenium
brew install chromedriver or on linux see (https://sites.google.com/a/chromium.org/chromedriver/downloads)
"""

import datetime
import argparse
from pyvirtualdisplay import Display
from selenium import webdriver

class WebTimings():

    timings = ["navigationStart", "fetchStart", "domainLookupStart", "domainLookupEnd", "connectStart",
               "connectEnd", "secureConnectionStart", "requestStart", "redirectStart", "redirectEnd",
               "responseStart", "responseEnd", "unloadEventStart", "unloadEventEnd", "domLoading",
               "domInteractive", "domContentLoadedEventStart", "domContentLoadedEventEnd" "domComplete",
               "loadEventStart", "loadEventEnd"]
    special = ["dnsTime", "connectionTime", "ttfbTime", "responseTime", "perceivedTime", "completeTime",
               "numberOfCssFiles", "numberOfCssFiles", "numberOfScriptFiles", "lastCssDownloaded", "lastImgDownloaded",
               "lastScriptDownloaded"]
    entries = ["resource"]

    def setUp(self):

        timings_string = ',\n'.join(self.timings) + ", " + ',\n'.join(self.special)

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-u', '--url', help='url to page you want to test', required=True)
        self.parser.add_argument('-v', '--value', help='value you want to get specifically [' + timings_string + ']',
                                 required=False)
        self.args = vars(self.parser.parse_args())

    def run(self):

	self.display = Display(visible=0, size=(1024, 768))
	self.display.start()

        self.driver = webdriver.Chrome() 

        self.result = Result()

        self.driver.get(self.args['url'])
        for timing in self.timings:
            self.result.timings[timing] = self.driver.execute_script("return window.performance.timing."+timing)

        for entry in self.entries:
            self.result.entries[entry] = \
                self.driver.execute_script('return window.performance.getEntriesByType("'+entry+'")')

    def present(self):
        self.result.calculate()
        if self.args["value"] is None:
        #if "value" not in self.args:
            print ""
            print " Web performance check"
            print ""
            print "------------------------------------------"
            print " Url: %s " % self.args['url']
            print "------------------------------------------"
            print ""
            print " Dns time: %s ms" % self.result.calculated["dnsTime"]
            print " Connection time: %s ms" % self.result.calculated["connectionTime"]
            print " Time to first byte: %s ms" % self.result.calculated["ttfbTime"]
            print " Response time: %s ms" % self.result.calculated["responseTime"]
            print " User perceived load time: %s ms" % self.result.calculated["perceivedTime"]
            print " Total load time: %s ms" % self.result.calculated["completeTime"]
            print ""
            print "------------------------------------------"
            print " Resources: "
            print "------------------------------------------"
            print ""
            print " Number of css files: %s" % self.result.calculated["numberOfCssFiles"]
            print " Css download complete after %.1f ms" % round(self.result.calculated["lastCssDownloaded"], 0)
            print " Number of image files: %s" % self.result.calculated["numberOfImgFiles"]
            print " Image download complete after %.1f ms" % round(self.result.calculated["lastImgDownloaded"], 0)
            print " Number of script files: %s" % self.result.calculated["numberOfScriptFiles"]
            print " Script download complete after %.1f ms" % round(self.result.calculated["lastScriptDownloaded"], 0)
            print ""
            print "------------------------------------------"
            print " Performance Details - Event Fire times"
            print "------------------------------------------"
            print ""
            for timing in self.timings:
                if self.result.timings[timing] is not None and self.result.timings[timing] > 0:
                    print " "+timing.capitalize()+": %s ms" % (self.result.timings[timing] -
                                                               self.result.timings["navigationStart"])
            print ""
            print " Done!"
            print ""

        else:
            if self.args["value"] in self.timings:
                print self.result.timings[self.args["value"]]
            elif self.args["value"] in self.result.calculated:
                print self.result.calculated[self.args["value"]]
            else:
                print "not found"

    def tearDown(self):
        self.driver.close()
        self.driver.quit()
        self.display.stop()

    def formatTimestamp(self, timestamp):
        objectDate = datetime.datetime.fromtimestamp(timestamp)
        return objectDate.strftime("%Y-%m-%d %H:%M:%S")


class Result(object):

    timings = {}
    calculated = {}
    entries = {}

    def calculate(self):

        self.calculated["responseTime"] = 0
        self.calculated["dnsTime"] = 0
        self.calculated["connectionTime"] = 0
        self.calculated["perceivedTime"] = 0
        self.calculated["completeTime"] = 0
        self.calculated["ttfbTime"] = 0

        self.calculated["numberOfCssFiles"] = 0
        self.calculated["lastCssDownloaded"] = 0
        self.calculated["numberOfImgFiles"] = 0
        self.calculated["lastImgDownloaded"] = 0
        self.calculated["numberOfScriptFiles"] = 0
        self.calculated["lastScriptDownloaded"] = 0

        self.calculated["responseTime"] = self.timings["responseEnd"] - self.timings["navigationStart"]
        self.calculated["dnsTime"] = self.timings["domainLookupEnd"] - self.timings["domainLookupStart"]
        self.calculated["connectionTime"] = self.timings["connectEnd"] - self.timings["connectStart"]
        self.calculated["perceivedTime"] = self.timings["loadEventStart"] - self.timings["responseStart"]
        self.calculated["completeTime"] = self.timings["loadEventEnd"] - self.timings["navigationStart"]
        self.calculated["ttfbTime"] = self.timings["responseStart"] - self.timings["connectEnd"]

        for resource in self.entries["resource"]:
            if resource['initiatorType'] == 'css':
                self.calculated["numberOfCssFiles"] += 1
                if self.calculated["lastCssDownloaded"] < resource['responseEnd']:
                    self.calculated["lastCssDownloaded"] = resource['responseEnd']
            elif resource['initiatorType'] == 'img':
                self.calculated["numberOfImgFiles"] += 1
                if self.calculated["lastImgDownloaded"] < resource['responseEnd']:
                    self.calculated["lastImgDownloaded"] = resource['responseEnd']
            elif resource['initiatorType'] == 'script':
                self.calculated["numberOfScriptFiles"] += 1
                if self.calculated["lastScriptDownloaded"] < resource['responseEnd']:
                    self.calculated["lastScriptDownloaded"] = resource['responseEnd']

if __name__ == '__main__':
    wt = WebTimings()
    wt.setUp()
    wt.run()
    wt.present()
    wt.tearDown()
