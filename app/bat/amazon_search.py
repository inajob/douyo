#! /usr/bin/python
# -*- coding: utf-8 -*-
from ctypes import *
import urllib
import socket,time
from datetime import datetime,timedelta
import re,random
from xml.dom import minidom, Node
import urllib,os,subprocess;

import analyzeTwit

#---------------------
def reply_to_list(xmlstr):
	#print  xmlstr.decode("utf-8","ignore")
	doc=minidom.parseString(xmlstr);
	items=doc.getElementsByTagName("Item");
	rets=[];
	for item in items:
		ret={"ASIN":-1,"Title":"","Creator":{},"URL":"","ImageURL":"","Manufacturer":"","Review":[]}
		for x in item.childNodes:
			if x.tagName=="ASIN":
				ret["ASIN"]=x.firstChild.nodeValue 
			elif x.tagName=="DetailPageURL":
				ret["URL"]=x.firstChild.nodeValue ;
			elif x.tagName=="MediumImage":
				for y in x.childNodes:
					if y.tagName=="URL":
						ret["ImageURL"]=y.firstChild.nodeValue ;
			elif x.tagName=="ItemAttributes":
				for y in x.childNodes:
					if y.tagName=="Title":
						ret["Title"]=y.firstChild.nodeValue ;
					elif y.tagName=="Creator":
						if ret["Creator"].has_key(y.getAttribute("Role")):
							ret["Creator"][y.getAttribute("Role")].append(y.firstChild.nodeValue)
						else:
							ret["Creator"][y.getAttribute("Role")]=[y.firstChild.nodeValue]
					elif y.tagName=="Manufacturer":
						ret["Manufacturer"]=y.firstChild.nodeValue ;
			elif x.tagName=="CustomerReviews":
				for r in x.childNodes:
					if(r.tagName == "Review"):
						tmp={}
						for y in r.childNodes:
							if y.tagName=="Rating":
								tmp["Rating"] = y.firstChild.nodeValue
							elif y.tagName == "Content":
								tmp["Content"] = y.firstChild.nodeValue
							elif y.tagName == "HelpfulVotes":
								tmp["HelpfulVotes"] = y.firstChild.nodeValue
						ret["Review"].append(tmp);
		rets.append(ret);
	return rets;
#---------------------

#--------------------
"""
def get_sha256sum(s):
	import popen2
	(o,i) = popen2.popen2("sha256sum");
	i.write(s);
	i.close();
	ret = o.read().split(" ")[0];
	i.close()
	return ret;
"""
def make_query(query):
	secret_key=os.environ["AMAZON_SECRET_KEY"];
	import base64
	from Crypto.Hash import HMAC
	from Crypto.Hash import SHA256
	
	options = {"Service":"AWSECommerceService",
		   "SubscriptionId":os.environ["AMAZON_SUBSCRIPTION_ID"],
		   "Operation":"ItemSearch",
		   "ItemSearch.Shared.ResponseGroup":"Small,Images,Reviews,ItemAttributes",
		   "ItemSearch.Shared.Keywords":query,
		   "ItemSearch.1.SearchIndex":"Books",
		   "ItemSearch.2.SearchIndex":"VideoGames",
		   "AssociateTag":os.environ["AMAZON_ASSOCIATE_TAG"],
		   "Timestamp":datetime.utcnow().isoformat()}
	kvlist = [x + "=" + urllib.quote_plus(options[x]) for x in sorted(options.keys())]
	parms = "&".join(kvlist)
	
	uri = "webservices.amazon.co.jp"
	end_point= '/onca/xml'
	strings = ['GET', uri, end_point, parms]
	digest = HMAC.new(secret_key, '\n'.join(strings), SHA256).digest()
	signature = base64.b64encode(digest)
	request_url = "http://%s%s?%s&Signature=%s" % (uri, end_point, parms, urllib.quote_plus(signature))
	return  request_url

def send_query(query):
    url = make_query(query.encode("utf8"))
    f = urllib.urlopen(url)
    reply=reply_to_list(f.read());
    f.close();
    print reply
    return reply

def strip_tags(str):
    str = re.sub(u"<[^>]+>",u" ",str);
    return str;

if __name__ == "__main__":
    rep=send_query(u"ルルーシュ");
    #print "===="
    print "hit" + str(len(rep))
    count = 0;
    max_rev=0;
    max_ind=-1;
    for i,x in enumerate(rep):
        if len(x["Review"])!=0:
            print x["Title"]
            print x["ASIN"]
            print len(x["Review"])
            print 
            revc = len(x["Review"])
            if max_rev < revc:
                max_rev=revc;
                max_ind=i;
            count += 1;
        else:
            pass
            #print "####"+x["Title"]
            #print 
    print str(count) + "/" +  str(len(rep))

    rep = rep[max_ind]
    print "==================="
    print rep["Title"]
    print rep["ASIN"]

    strl=[];
    for x in rep["Review"]:
        #print "==============================="
        #print strip_tags(x["Content"])
        strl.append(strip_tags(x["Content"]));

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
