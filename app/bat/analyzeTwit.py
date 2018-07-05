#! /usr/bin/python
# -*- coding: utf-8 -*-
from ctypes import *
import urllib
import socket,time
from datetime import datetime,timedelta
import re,random
import simplejson
import cPickle as pickle
import codecs
import sys
import os
import itertools
from pymecab.pymecab import PyMecab


baseURI="http://twitter.com/statuses/"

import twoauth
#################################
## initialize oauth
#################################
twitterapi = twoauth.api(
	os.environ["TWITTER_CONSUMER_KEY"],
	os.environ["TWITTER_CONSUMER_SECRET"],
	os.environ["TWITTER_ACCESS_KEY"],
	os.environ["TWITTER_ACCESS_SECRET"]
);

###################################################
##       Post Twit
###################################################
def post_twit(par):
        dto= socket.getdefaulttimeout();
        socket.setdefaulttimeout(6);
        url=baseURI;
        postData={};
        postData["status"]=par
        postData["source"]="douyo"
        params = "status="+urllib.quote(postData["status"].encode("utf-8"))+"&"
        params = params+("source="+postData["source"])
        try:
                try:
                    #f =urllib.urlopen(url+"update.json",params)
		    twitterapi.status_update(postData["status"].encode("utf-8"));
                    #print f.read();
                except :
                    print "time out ?"
        finally:
            socket.setdefaulttimeout(dto)

###################################################
##       Get Public Timeline
###################################################
def gets_twit():
        dto= socket.getdefaulttimeout();
        socket.setdefaulttimeout(32);
        url=baseURI;
        params=""
        params = params+("source=Mai")
        obj=[];
        s=""
        try:
                try:
                    #f =urllib.urlopen(url+"public_timeline.json?"+params)
                    #s=f.read();
                    #obj=simplejson.loads(s);
		    obj= twitterapi.trends_place() #simplejson.loads(s);
		    #print s
                except Exception,e:
                    print "time out ? get twit"
                    print sys.exc_info()
                    print e.read()
                    #print (s);
        finally:
            socket.setdefaulttimeout(dto)
        ret=[];
        for x in obj[0]['trends']:
            #print x["user"]["name"]
            #print x["text"];
            #print "@@",x;
            if(x["name"]):
                ret.append((x["name"],"name",'id'))
        time.sleep(1)
        return ret;

def get_trends():
        dto= socket.getdefaulttimeout();
        socket.setdefaulttimeout(32);
        url=baseURI;
        params=""
        params = params+("source=Mai")
        obj=[];
        s=""
        try:
                try:
		    obj= twitterapi.trends_place() #simplejson.loads(s);
		    #print s
                except Exception,e:
                    print "time out ? get trends"
                    print sys.exc_info()
                    print e.read()
                    #print (s);
        finally:
            socket.setdefaulttimeout(dto)
        ret=[];
        print obj;
        for x in obj[0]["trends"]:
            #print x["user"]["name"]
            #print x["text"];
            #print "@@",x;
            if(x["name"]):
                ret.append((x["name"]))
        time.sleep(1)
        return ret;


###################################################
##       Get followers Timeline
###################################################
def gets_friend(page=1):
        dto= socket.getdefaulttimeout();
        socket.setdefaulttimeout(32);
        url=baseURI;
        params=""
        obj=[];
        s=""
        try:
                try:
                    #f =urllib.urlopen(url+"followers.json?page="+str(page))
                    #s=f.read();
                    #print s
		    obj= twitterapi.status_followers(page=str(page));#simplejson.loads(s);
                except :
                    print "time out ? gets_friend"
                    #print (s);
        finally:
            socket.setdefaulttimeout(dto)
        ret=[];
	
        for x in obj:
            #print x;
            if x==[]:
                continue;

            if(x.has_key("status") and x["status"].has_key("text")):
                ret.append((x["status"]["text"],x["name"],x["status"]["id"]))
        time.sleep(1)
        return ret;
###################################################
##       Get replies Timeline
###################################################
def gets_replies(index=-1,page=1):
        dto= socket.getdefaulttimeout();
        socket.setdefaulttimeout(32);
        url=baseURI;
        params=""
        obj=[];
        s=""
        try:
                try:
			id="";
			if index!=-1:
				#id = "since_id="+str(index)+"&";
				obj = twitterapi.mentions(since_id=str(index));
			else:
				obj = twitterapi.mentions();
			#f =urllib.urlopen(url + "replies.json?" + id + "page=" + str(page))
			#s=f.read();
                        #print id
			#obj=simplejson.loads(s);
                except :
                    print "time out ?"
                    #print (s);
        finally:
            socket.setdefaulttimeout(dto)
        ret=[];
	
        for x in obj:
            print x;
            if x==[]:
                continue;
            if x.has_key("text"):
                ret.append((x["text"],x["user"]["screen_name"],x["id"]))
        time.sleep(1)
        return ret;

###################################################
##       Get User Timeline
###################################################
def gets_user(user,page=1):
        dto= socket.getdefaulttimeout();
        socket.setdefaulttimeout(32);
        url=baseURI;
        params=""
        obj=[];
        s=""
        try:
                try:
                    #f =urllib.urlopen(url+"user_timeline/"+user+".json?page="+str(page))
                    #s=f.read();
                    #print s
                    obj= twitterapi.user_timeline(user,page=page);  #simplejson.loads(s);
		    print obj
                except Exception,e:
                    print "time out ?"+ str(e)
                    #print (s);
        finally:
            socket.setdefaulttimeout(dto)
        ret=[];
	
        for x in obj:
            #print x;
            if x==[]:
                continue;

            #if(x.has_key("status") and x["status"].has_key("text")):
            #    ret.append(x["status"]["text"])
            if(x.has_key("text")):
                ret.append((x["text"],x["user"]["screen_name"],x["id"]))
        time.sleep(1)
        return ret;

###################################################

def loadlib():
    # ライブラリを ctypes を使って読み込み
    lib = cdll.LoadLibrary(libpath)
    return lib
# 表層形\t品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
def parse(lib,s):
    mecab = PyMecab()
    print s;
    s = s.encode(m_code,"ignore")
    cl=[];
    for token in mecab.tokenize(s):
      cl.append((
        token.surface.decode("utf8") if token.surface else "",
        token.pos1.decode("utf8") if token.pos1 else "",
        token.pos2.decode("utf8") if token.pos2 else "",
        token.pos3.decode("utf8") if token.pos3 else "",
        token.pos4.decode("utf8") if token.pos4 else "",
        token.conjugation_form.decode("utf8") if token.conjugation_form else "",
        token.conjugation_type.decode("utf8") if token.conjugation_type else "",
        token.base_form.decode("utf8") if token.base_form else "",
        token.reading.decode("utf8") if token.reading else "",
        token.pronunciation.decode("utf8") if token.pronunciation else ""
      ));
    return cl;

    """
    # 解析器初期化用の引数を指定（-Owakati で分かち書き)
    argc = c_int(2)
    argv = (c_char_p * 2)("mecab", "")

    # 解析器のオブジェクトを作る
    tagger = lib.mecab_new(argc, argv)
    s = s.encode(m_code,"ignore")
    s = lib.mecab_sparse_tostr(tagger,s);
    ret = c_char_p(s).value
    retl = ret.decode(m_code,"ignore").split("\n");
    cl=[];
    for x in retl:
        a = x.split("\t")
        if(len(a)==1):
            continue
        b = a[1].split(",");
        cl.append([a[0]] + b)
    return cl
    """
###################################################
def ngwords(s):
    s = re.sub("http://.*","",s);
    s = re.sub(u"L:.*","",s);
    s = re.sub(u"@[a-zA-Z0-9_]*","",s);
    s = re.sub(u"[a-zA-Z0-9!#%=.\[\]]{2,}","",s)
    s = re.sub(u"\*[^*]+\*","",s);
    s = re.sub(u"\(",u"（",s);
    s = re.sub(u"\)",u"）",s);
    
    # and convert
    s = re.sub(u"&lt;",u"<",s);
    s = re.sub(u"&gt;",u">",s);
    s = re.sub(u"&amp;",u"&",s);
    
    return s;
###################################################
def ngwords2(s):
    s = re.sub("http://.*","",s);
    s = re.sub(u"@[a-zA-Z0-9_]*","",s);
    s = re.sub(u"\*[^*]+\*","",s);
    # and convert
    s = re.sub(u"&lt;",u"<",s);
    s = re.sub(u"&gt;",u">",s);
    s = re.sub(u"&amp;",u"&",s);
    s = re.sub(u"#.*",u"",s); # for comment
    s = re.sub(u"//.*",u"",s); # for comment
    return s;

def getlink(s):
    s = re.findall(u"@[a-zA-Z0-9_]*",s)
    return s

def dump(l,sep=",",depth=0):
    for x in l:
        if type(x)==list:
            sys.stdout.write("[")
            dump(x,sep,depth+1)
            sys.stdout.write("]")
            if depth==0:
                print ""
        else:
            try:
                sys.stdout.write(x.encode(console_code,"ignore")+sep)
            except:
                sys.stdout.write(x+sep)
def convert(l):
    ret = [];
    pre="";
    for x in l:
        tmp = "";
        for y in x:
            tmp += y[0];
        if(tmp==pre):
            continue;  #not doubling
        pre=tmp;
        ret.append(tmp)
    return ret;
def filter_koyu(l):
    ret=[];
    for x in l:
        if x[2]==u"固有名詞":
            ret.append(x);
    return ret

def filter_simple(l):
    ret=[];
    tmp = [];
    startf = False;
    """
    for x in l:
        #print x[0]
        if x[1]==u"名詞" and x[2]!=u"非自立" and len(x[0])>1:
		tmp.append(x[0]);            
		startf = True;
        elif x[1]==u"接頭詞":
                tmp.append(x[0])
		startf = True;
        #elif x[1]==u"連体詞":
        #        ret.append([x[0],x[1]])
        elif x[1]==u"形容詞" and x[2]!=u"非自立":
                tmp.append(x[0])
		startf = True;
        #elif startf and x[1]==u"助詞" and (x[2]==u"連体化"):  #  or x[2]==u"副助詞／並立助詞／終助詞"
        #        tmp.append(x[0])
        #elif startf and x[1]==u"助動詞" and (x[6]==u"体言接続"):
        #        tmp.append(x[0])
	else:
		if tmp!=[]:
			#tmp.reverse();
			ret.append(tmp);
		tmp = [];
		startf = False;
#    print len(ret)
#    print ret
"""
    for x in l:
      if(len(x[0]) > 2):
        ret.append([x[0]]);
    return ret

def filter_meishi(l):
    ret=[];
    i=0;

    tmp=[]
    for x in l:
        if x[1]==u"名詞" and x[2]!=u"非自立":
            tmp.append([x[0],x[1],x[2]])
            
        elif x[1]==u"接頭詞":
                tmp.append([x[0],x[1]])
        
        #elif x[1]==u"連体詞":
        #        tmp.append([x[0],x[1]])
        elif x[1]==u"形容詞" and x[2]!=u"非自立":
                tmp.append([x[0],x[1]])
            
        elif x[1]==u"助詞" and (x[2]==u"連体化"):  #  or x[2]==u"副助詞／並立助詞／終助詞"
                tmp.append([x[0],x[1]])
        elif x[1]==u"助動詞" and (x[6]==u"体言接続"):
                tmp.append([x[0],x[1]])
        else:
            if(len(tmp)!=0):
                start=0;
                end=len(tmp)
                for y in tmp:
                    if(((y[1]==u"名詞" and y[2]==u"接尾") or y[1]!=u"名詞") and y[1]!=u"接頭詞" and y[1]!=u"連体詞" and y[1]!=u"形容詞"):
                        start+=1;
                    else:
                        break;
                tmp.reverse();
                for y in tmp:
                    if(y[1]!=u"名詞" and y[1]!=u"連体詞" and y[1]!=u"形容詞"):
                        end-=1;
                    else:
                        break;
                tmp.reverse();
                
                if(end-start>=2):   #not regist only 1word
                    ret.append(tmp[start:end])
                
                tmp=[]
    if(len(tmp)!=0):
                ret.append(tmp)
                tmp=[]        
    return ret

def meishi_list_sort(l):
    l.sort(lambda a,b:-len(a)+len(b));
    # sort is change own


def random_choice(num,l):
    #a = gets_friend();  # friend_timeline
    #a += gets_twit();   # public_timeline
    a = gets_twit();   # public_timeline
    #a += gets_twit()
    #a = gets_friend(2);
    meishil=[]
    count = {};
    for x in a:
        llist=getlink(x[0])
        s = ngwords(x[0]);
        pl = parse(l,s)
	for n in pl:
          print ','.join(n)
        kl = filter_koyu(pl)
	sl = filter_simple(pl)
	for x in sl:
		for y in x:
			count[y] = count.get(y,0) + 1
	for x in kl:
		count[x[0]] = count.get(x[0],0) + 1
        meishil+=sl
    
    for k,v in sorted(count.items(), key=lambda v: v[1]):
        print k,v
	
    meishil.sort(lambda a,b:-len(a)+len(b));
    #dump(meishil)
    random.shuffle(meishil)
    ret = []
    tmp = "";
    for x in meishil:
	    for y in x:
		    tmp += y;
	    if(len(tmp)>=3): # words length 
		    ret.append(tmp);
	    tmp="";
    return ret[0:num];


# ライブラリの場所を指定
libpath = '/usr/lib/x86_64-linux-gnu/libmecab.so.2'
#libpath = 'C:/soft/program/MeCab/bin/libmecab.dll'
#m_code="eucjp";
m_code="utf8";
console_code="utf8";

if __name__ == "__main__":
    ###################################################
    #a = gets_user("ina_ani");
    #a = a + gets_user("ina_ani",2);
    a = gets_friend();
    a = gets_friend(2);
    """
    f = file("tmp.pkl","wb");
    pickle.dump(a,f);
    f.close();
    """
    ###########################
    # string list -> ngwords -> parse -> filter_meishi -> meishi_list_sort() -> convert
    ###########################

    sys.stdout = codecs.getwriter(console_code)(sys.stdout)
    """
    f = file("tmp.pkl","rb")
    a = pickle.load(f);
    f.close();
    """
    l=loadlib();

    meishil=[]
    for x in a:
        llist=getlink(x)
        s = ngwords(x);
	print
        pl = parse(l,s)
        #dump(pl)
        #print "#####"
	
        kl = filter_koyu(pl)
        #dump(kl)
        
	#print llist
        #ml = filter_meishi(pl)
        #dump(ml)
	
	sl = filter_simple(pl)
	#dump(sl)
        #print
        #print s.encode(console_code,"ignore")
        
        if sl!=[]:
		meishil += (sl)#sl+kl
    meishil.sort(lambda a,b:-len(a)+len(b));
    #dump(meishil)
    #dump(convert(meishil))
    
    print meishil
    #r = random.choice(meishil)
    #r = meishil[0]
    #print "=="
    #print r;
    #print "=="
    for x in meishil:
	    for y in x:
		    sys.stdout.write(y);
	    print
    
