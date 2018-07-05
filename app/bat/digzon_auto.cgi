#! /usr/bin/python
# -*- coding: utf-8 -*-
# coding: utf-8 

import re,os,time,sys,glob
import time,datetime
import codecs,random

import amazon_search
import analyzeTwit
import booklog
import simplejson
import cgi

basePath="/app/data/"

def err_page(err):
    print "Content-Type: text/html;charset=utf-8\n\n"
    print err
    print make_form()

def make_form():
    return """
    <form action="digzon_k.cgi" method="get">
        keyword:<input type="text" name="key" size="20" />
    </form>
    """
def update_setting(id,time):
    print "update",id
    f = open(basePath + "id_store.txt","w");
    f.write(simplejson.dumps({"last_id":id,"last_timer":time}));
    f.close();

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
l = analyzeTwit.loadlib();

keys=[]
postfix = " ";

settings={"last_id":-1,"last_timer":0};

if(os.path.exists(basePath + "id_store.txt")):
    f = open(basePath + "id_store.txt","r")
    settings = simplejson.loads(f.read());
    f.close();

if time.time()-settings["last_timer"] < 60*4: # 5minutes
    print "stop at 5minutes check"
    sys.exit(); # shorttime exit
"""
reps = analyzeTwit.gets_replies(settings["last_id"]); # index,page  getReplies
reps.reverse();
print reps
rsplit = re.compile(",|　| ");  # separate char
for x in reps:
    #f = open(basePath + "id_store.txt","w");
    print x[2] , "@" + x[1] , "[" + analyzeTwit.ngwords2(x[0]) + "]"
    keys = rsplit.split(analyzeTwit.ngwords2(x[0]));
    #f.write(simplejson.dumps( x[2] ));
    #f.close();
    #update_setting(x[2],settings["last_timer"]);
    settings["last_id"] = x[2]
    postfix = " from @" + x[1] + " "
    break;
#sys.exit()
"""

# stop in electron now 09/02
"""
if keys==[]:      # if no request search @tnd
    f = open(basePath + "last_asin_from_tnd.txt")
    s = simplejson.loads(f.read());
    f.close();
    f = open("/var/www/html/tnd/current.json");
    objs = simplejson.loads(f.read());
    f.close();
    last = objs["data"][-1]["amz"]["ASIN"];
    if last!= s["asin"]:
        keys.append(last);
        postfix = " from @" + objs["data"][-1]["user"]["screen_name"] + " via @tnd "
        f = open(basePath + "last_asin_from_tnd.txt","w");
        f.write(simplejson.dumps({"asin":last}));
        f.close();
"""

print "get trends";
if keys==[]:      # if no request
    if time.time()-settings["last_timer"] < 60*60: # 60minutes
        print "stop at 60minutes check"
        sys.exit(); # shorttime exit
    keys = analyzeTwit.random_choice(20,l);
#if keys ==[]:
#  keys = analyzeTwit.get_trends();
flag = False


max_rev=0;
max_ind=-1;
wvect=[[0,-1]]

f = open(basePath+"contents/files.json","r+");
files = simplejson.loads(f.read());
f.close();

for x in keys:
    print "try...",x
    rep=amazon_search.send_query(x);
    if len(rep)==0:
        print "not hit amazon"
        continue;
    max_rev=0;
    max_ind=-1;
    wvect=[[0,-1]]
    for i,x in enumerate(rep):
        wvect.append([1,i])
        if len(x["Review"])!=0:
            revc = len(x["Review"])
            tmp=0;
            for y in x["Review"]:
                tmp += int(y["HelpfulVotes"])
            tail = wvect[-1][0]
            wvect.append([1.0*tmp/revc+tail,i])
            #if max_rev < 1.0*tmp/revc:
            #    max_rev=revc;
            #    max_ind=i;
    if(len(wvect)==1):
        err_page("not found");
        continue;

    #  weight map
    max_w = wvect[-1][0]
    hit=random.uniform(0, max_w)
    for x in wvect:
        if hit < x[0]:
            max_ind = x[1]
            break;
    rep = rep[max_ind]
    cl=[]
    title = rep["Title"]
    asin = rep["ASIN"]

    strl=[];
    for x in rep["Review"]:
        strl.append(amazon_search.strip_tags(x["Content"]));
    for x in booklog.send_query(asin):
        strl.append(booklog.strip_tags(x));
    meishil = []
    for x in strl:
        s = analyzeTwit.ngwords(x);
        pl = analyzeTwit.parse(l,s)
        ml = analyzeTwit.filter_meishi(pl)
        meishil += ml
    analyzeTwit.meishi_list_sort(meishil);
    if(len(meishil)==0):
        print "error not tag"
        continue;
        #sys.exit();

    
    sameFile = False
    for x in files:
        if x=="data/"+asin+".xml":
            print "same file"
            sameFile = True;
    if sameFile:
        continue;

    flag=True
    break;
if flag==False:
    print "error nothing to do"
    sys.exit()
revs="<div class='list'><ul>\n"
for x in analyzeTwit.convert(meishil):
    revs += "<li>"+x+"</li>\n"
revs += "</ul></div>"#+str(wvect)+":"+str(hit)


count = 0
dig=""
digl = [];
count_n = 0;
for x in analyzeTwit.convert(meishil):
    count += len(x)+2
    count_n += 1;
    if(count > 50):
        count -= len(x)+2
        continue;
    if count_n <= 2:
        dig += u"["+x+u"]"
    digl.append(x);
#if(len(title)>=20):
#    dig = dig +u" → "+ title[:20] +u".."
#else:
#    dig = dig +u" → "+ title

url = "http://douyo.inajob.tk/data/"+asin+".xml"
print dig +postfix + url,len(dig)
update_setting(settings["last_id"],time.time());
#sys.exit(0)
analyzeTwit.post_twit(dig+ postfix +url);

#print dig
#print rep["URL"],title,asin,rep["ImageURL"]
tags = "";
for x in digl:
    tags +="<tag>" + cgi.escape(x).replace("\"","") +"</tag>"
s = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="page.xsl" ?>
<douyo>
  <data revision="%s" title="%s" image="%s" url="%s">
    <tags>
       %s
    </tags>
  </data>
</douyo>"""  % (datetime.datetime.now().isoformat(),cgi.escape(title).replace("\"",""),rep["ImageURL"],rep["URL"].replace("&","&amp;"),tags)

print s


f = open(basePath+"contents/"+asin+".xml","w");
f.write(s.encode("utf-8"));
f.close();

files.append("data/"+asin+".xml");
files = files[-25:]
s = simplejson.dumps(files);
f = open(basePath+"contents/files.json","w");
f.write(s);
f.close();

print "write "+asin;
