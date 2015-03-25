#!/usr/bin/env python
# coding: utf-8

"""
Using the navigation timings api, see descriptions at the bottom.
pip install selenium
brew install chromedriver or on linux see (https://sites.google.com/a/chromium.org/chromedriver/downloads)
"""

import os
import csv
import time
import ordereddict
import datetime
import argparse
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException


class WebTimings():
    def __init__(self):
        self.timings = ["navigationStart", "redirectStart", "redirectEnd", "fetchStart", "domainLookupStart",
                        "domainLookupEnd", "connectStart", "connectEnd", "secureConnectionStart", "requestStart",
                        "responseStart", "responseEnd", "unloadEventStart", "unloadEventEnd", "domLoading",
                        "domInteractive", "domContentLoadedEventStart", "domContentLoadedEventEnd" "domComplete",
                        "loadEventStart", "loadEventEnd"]
        self.special = ["Network", "Browser", "Server"]
        self.entries = ["resource"]

    def setUp(self):

        timings_string = ',\n'.join(self.timings) + ", " + ',\n'.join(self.special)

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-u', '--url', help='url(s) to page you want to test', required=True)
        self.parser.add_argument('-v', '--value', help='value you want to get specifically [' + timings_string + ']',
                                 required=False)
        self.parser.add_argument('-d', '--detail', help='detailed response [true/false]',
                                 required=False)
        self.parser.add_argument('-r', '--runs', help='multiple runs, get average [true/false]',
                                 required=False)
        self.parser.add_argument('-c', '--csv', help='output as csv file (webtimings.csv) [true/false]',
                                 required=False)
        self.args = vars(self.parser.parse_args())

    def readystate_complete(self, d):
        return d.execute_script("return document.readyState") == "complete"

    def run(self):

        try:
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()
        except Exception:
            pass

        #For pycharm
        #chromedriver = "/usr/local/Cellar/chromedriver/2.13/bin/chromedriver"
        #os.environ["webdriver.chrome.driver"] = chromedriver
        #self.driver = webdriver.Chrome(chromedriver)
        self.driver = webdriver.Chrome()
        self.results = []

        urls = self.args['url'].split(',')

        for url in urls:
            try:
                result = self.getUrl(url)
                self.results.append(result)

                if result.categoryUrl != "":
                    result = self.getUrl(result.categoryUrl)
                    self.results.append(result)

                exit

            except Exception as e:
                pass

    def getUrl(self, url):
        result = Result()
        result.url = url
        result.categoryUrl = ""
        if self.args['runs'] is not None:
            runs = int(float(self.args['runs']))
            #run multiple
            for x in range(0, runs):

                try:
                    self.driver.get(url)

                    WebDriverWait(self.driver, 15).until(self.readystate_complete)
                except WebDriverException:
                    pass

                for timing in self.timings:
                    if result.timings[timing] is None:
                        result.timings[timing] = 0
                    result.timings[timing] = result.timings[timing] + \
                        self.driver.execute_script("return window.performance.timing." + timing)

                for entry in self.entries:
                    if result.entries[entry] is None:
                        result.entries[entry] = 0
                    result.entries[entry] = result.entries[entry] + self.driver.execute_script(
                        'return window.performance.getEntriesByType("' + entry + '")')

            # count averages
            for timing in self.timings:
                result.timings[timing] = int(result.timings[timing] / runs)

            for entry in self.entries:
                result.entries[entry] = int(result.entries[entry] / runs)

        else:
            try:
                self.driver.get(url)

                WebDriverWait(self.driver, 15).until(self.readystate_complete)
            except WebDriverException:
                pass

            for timing in self.timings:
                result.timings[timing] = self.driver.execute_script(
                    "return window.performance.timing." + timing)

            for entry in self.entries:
                result.entries[entry] = self.driver.execute_script(
                    'return window.performance.getEntriesByType("' + entry + '")')

        elements = self.driver.find_elements_by_css_selector("ul li ul li a")
        for element in elements:
            result.categoryUrl = element.get_attribute("href")
            break

        result.calculate()
        return result


    def present(self):
        print ""
        print "------------------------------------------"
        print " Web performance check"
        print "------------------------------------------"
        print ""

        if self.args["csv"] is not None and self.args["csv"] == "true":
            self._presentCSV()
            print "Outputed values in webtimings.csv"
        else:
            self._presentTerminal()

    def _presentCSV(self):

        self.detailed = False
        if self.args["detail"] is not None and self.args["detail"] == "true":
            self.detailed = True

        namesPrinted = False
        timestamp = int(time.time())
        data = []

        if self.args["value"] is None:

            for result in self.results:
                if self.detailed:
                    if not namesPrinted:
                        row = ["Url", "Timestamp"]
                        for key, value in result.calculated.iteritems():
                            if key is not "Network" and key is not "Server" and key is not "Browser":
                                row.append(key),
                        data.append(row)
                        namesPrinted = True
                    row = [result.url, timestamp]
                    for key, value in result.calculated.iteritems():
                        if key is not "Network" and key is not "Server" and key is not "Browser":
                            row.append(value)

                    data.append(row)
                else:
                    if not namesPrinted:
                        data.append(["Url", "Timestamp", "Total", "Network", "Server", "Browser"])
                        namesPrinted = True
                    print data.append([result.url, timestamp, result.calculated["Total"], result.calculated["Network"],
                                       result.calculated["Server"], result.calculated["Browser"]])
        else:
            for result in self.results:

                if not namesPrinted:
                    data.append(["Url", self.args["value"]])
                    namesPrinted = True
                row = [result.url]
                if self.args["value"] in result.calculated:
                    row.append(result.calculated[self.args["value"]])
                else:
                    row.append("")
                data.append(row)

        with open('webtimings.csv', 'wb') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(data)

    def _presentTerminal(self):

        self.detailed = False
        if self.args["detail"] is not None and self.args["detail"] == "true":
            self.detailed = True

        w = 15
        namesPrinted = False
        timestamp = int(time.time())

        if self.args["value"] is None:

            for result in self.results:
                if self.detailed:
                    if not namesPrinted:
                        print self._tidyPrint("Url", 50), \
                            self._tidyPrint("Timestamp", w),
                        for key, value in result.calculated.iteritems():
                            if key is not "Network" and key is not "Server" and key is not "Browser":
                                print self._tidyPrint(key, w),
                        print ""
                        namesPrinted = True
                    print self._tidyPrint(result.url, 50), \
                        self._tidyPrint(timestamp, w),
                    for key, value in result.calculated.iteritems():
                        if key is not "Network" and key is not "Server" and key is not "Browser":
                            print self._tidyPrint(value, w),
                    print ""
                else:
                    if not namesPrinted:
                        print self._tidyPrint("Url", 50), \
                            self._tidyPrint("Timestamp", w), \
                            self._tidyPrint("Total", w), \
                            self._tidyPrint("Network", w), \
                            self._tidyPrint("Server", w), \
                            self._tidyPrint("Browser", w)
                        namesPrinted = True
                    print self._tidyPrint(result.url, 50), \
                        self._tidyPrint(timestamp, w), \
                        self._tidyPrint(result.calculated["Total"], w), \
                        self._tidyPrint(result.calculated["Network"], w), \
                        self._tidyPrint(result.calculated["Server"], w), \
                        self._tidyPrint(result.calculated["Browser"], w)
        else:
            for result in self.results:

                if not namesPrinted:
                    print self._tidyPrint("Url", 30), \
                        self._tidyPrint(self.args["value"], w)
                    namesPrinted = True
                print self._tidyPrint(result.url, 30),
                if self.args["value"] in result.calculated:
                    print self._tidyPrint(result.calculated[self.args["value"]], w)
                else:
                    print self._tidyPrint("-", w)

    def _tidyPrint(self, value, size):
        if isinstance(value, str):
            value = value.capitalize()
        if isinstance(value, int):
            if value < 0:
                value = "-"
            elif value > 10000000:
                value = str(value)
            else:
                value = str(value) + " ms"
        if isinstance(value, float):
            value = int(value)
            if value < 0:
                value = "-"
            elif value > 10000000:
                value = str(value)
            else:
                value = str(value) + " ms"
        if len(value) > size:
            value = value[:size - 2] + '..'
        return value.ljust(size)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

        try:
            self.display.stop()
        except Exception:
            pass

    def formatTimestamp(self, timestamp):
        objectDate = datetime.datetime.fromtimestamp(timestamp)
        return objectDate.strftime("%Y-%m-%d %H:%M:%S")


class Result(object):
    def __init__(self):
        self.timings = ordereddict.OrderedDict()
        self.calculated = ordereddict.OrderedDict()
        self.entries = ordereddict.OrderedDict()
        self.url = ""

    def calculate(self):
        #self.calculated = self.timings

        #print self.timings["loadEventEnd"]

        self.calculated["Network"] = self.timings["connectEnd"] - self.timings["navigationStart"]
        self.calculated["Server"] = self.timings["responseEnd"] - self.timings["requestStart"]
        self.calculated["Browser"] = self.timings["loadEventEnd"] - self.timings["responseEnd"]
        self.calculated["Total"] = self.timings["loadEventEnd"] - self.timings["navigationStart"]

        self.calculated["Start"] = 0
        if "unloadEnd" in self.timings and "unloadStart" in self.timings:
            self.calculated["Unload"] = self.timings["unloadEnd"] - self.timings["unloadStart"]
        self.calculated["Redirect"] = self.timings["redirectEnd"] - self.timings["redirectStart"]
        self.calculated["Cache"] = self.timings["domainLookupStart"] - self.timings["fetchStart"]
        self.calculated["Dns"] = self.timings["domainLookupEnd"] - self.timings["domainLookupStart"]
        self.calculated["Tcp"] = self.timings["connectEnd"] - self.timings["connectStart"]
        self.calculated["Request"] = self.timings["responseStart"] - self.timings["requestStart"]
        self.calculated["Response"] = self.timings["responseEnd"] - self.timings["responseStart"]
        self.calculated["Processing"] = self.timings["loadEventStart"] - self.timings["domLoading"]
        self.calculated["OnLoad"] = self.timings["loadEventEnd"] - self.timings["loadEventStart"]


        """for resource in self.entries["resource"]:
            if resource['initiatorType'] == 'css':
                if self.calculated["Css"] < resource['responseEnd']:
                    self.calculated["Css"] = resource['responseEnd']
            elif resource['initiatorType'] == 'img':
                if self.calculated["Images"] < resource['responseEnd']:
                    self.calculated["Images"] = resource['responseEnd']
            elif resource['initiatorType'] == 'script':
                if self.calculated["Scripts"] < resource['responseEnd']:
                    self.calculated["Scripts"] = resource['responseEnd']"""


if __name__ == '__main__':
    wt = WebTimings()
    wt.setUp()
    wt.run()
    wt.present()
    wt.tearDown()
