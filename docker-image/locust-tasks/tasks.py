#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 13:13:44 2020

@author: santiagorinconmartinez
"""

import time
from locust import HttpLocust, TaskSet, task, between
import random
import re
from xeger import Xeger


REGEX_URL="^(?:http|ftp)s?://(?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+(?:[A-Za-z]{2,6}\.?|[A-Za-z0-9-]{2,}\.?)|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$"

class MetricsTaskSet(TaskSet):
    wait_time = between(1, 2)
    
    def generateUID(self):
        x = Xeger(limit=8)
        return x.xeger("[A-Z0-9]+")
    
    def generatePn(self):
        return "checkout"
    
    def generatePurl(self):
        x = Xeger(limit=100)
        url = x.xeger(REGEX_URL)
        if self._is_valid_url(url):
            return url
        else:
            raise AssertionError('URL invalid')
            
    def generateProducts(self):
        x = Xeger(limit=100)
        return x.xeger("([A-Za-z0-9]+;)+([A-Za-z0-9])").split(";")
    
    def generateProductsRequest(self):
        products = random.choice(self.products)
        contin = random.choice(['Y', 'N'])
        while contin=='Y':
            products = products+";"+random.choice(self.products)
            contin = random.choice(['Y', 'N'])
        return products
    
    def generateParams(self):
        uid=self.uid
        pn=self.generatePn()
        purl=self.generatePurl()
        e="pl"
        pr=self.generateProductsRequest()
        return "uid={uid}&pn={pn}&purl={purl}&e={e}&pr={pr}".format(uid=uid,
                                                                     pn=pn,
                                                                     purl=purl,
                                                                     e=e,
                                                                     pr=pr)

    @staticmethod
    def _is_valid_url(url):
        """
        Check if a url is a valid url.
        Used to filter out invalid values that were found in the "href" attribute,
        for example "javascript:void(0)"
        taken from https://stackoverflow.com/questions/7160737
        :param url: url to be checked
        :return: boolean indicating whether the URL is valid or not
        """
        regex = re.compile(REGEX_URL, re.IGNORECASE)
        return re.match(regex, url) is not None
    
    @task
    def ask_for_pixel(self):
        self.client.get("/pixel.png?{}".format(self.generateParams()))

    def on_start(self):
        self.uid = self.generateUID()
        self.products = self.generateProducts()
        
class MetricsLocust(HttpLocust):
    task_set = MetricsTaskSet