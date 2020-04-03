import urllib
import json

def make_query(query):
    return "http://web.inajob.ml/ad/amz.php?q=" + urllib.quote_plus(query)

def send_query(query):
    url = make_query(query.encode("utf8"))
    print url
    f = urllib.urlopen(url)
    reply=f.read();
    f.close();
    return json.loads(reply)


if __name__ == "__main__":
    print send_query("test")
