#! /usr/bin/python
# -*- coding: utf-8 -*-
from ctypes import *
import urllib2
import socket,time
from datetime import datetime,timedelta
import re,random
import urllib,os,subprocess;

from BeautifulSoup import BeautifulSoup

import analyzeTwit

def send_query(asin):
    ret = [];
    opener = urllib2.build_opener()
    #opener.addheaders = [('User-agent', 'Python2.4.3'),('Accept-Language','ja,en-us;q=0.7,en;q=0.3')]
    srcHtml = opener.open('http://booklog.jp/item/1/' + asin).read()
    #print srcHtml
    #soup = BeautifulSoup(srcHtml)
    #desc = soup.findAll("p",{"itemprop" : "description"});
    #for x in desc:
    #  ret.append(x.decodeContents());

    r = re.compile(r'"description">(.*?)</p>', re.S);
    li = r.findall(srcHtml);
    for x in li:
      ret.append(x.decode("utf8"));
    return ret;

def strip_tags(str):
    str = re.sub(u"<[^>]+>",u" ",str);
    return str;

if __name__ == "__main__":
    ret=send_query(u"475753597X");
    #print "===="

    strl=[];
    for x in ret:
        #print "==============================="
        strl.append(strip_tags(x));

    l = analyzeTwit.loadlib();
    meishil = []
    for x in strl:
        s = analyzeTwit.ngwords(x);
        pl = analyzeTwit.parse(l,s)
        ml = analyzeTwit.filter_meishi(pl)
        meishil += ml
    analyzeTwit.meishi_list_sort(meishil);
    for x in analyzeTwit.convert(meishil):
        print x
