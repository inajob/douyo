function bindElements(datas,pelm){
    var elm = null;
    var ret = {};
    var postFix = "_tmpl";
    var j,i;
    pelm.id="";
    if(datas instanceof Array){
	var ls = pelm.childNodes;
	for(i=0;i<ls.length;i++){
	    for(j=0;j<datas.length;j++){
		if(ls[i].id == datas[j] + postFix){
		    ret[datas[j]] = ls[i]; // match?
		    ls[i].id=""
		    break;
		}
	    }
	    var cn = ls[i].childNodes;
	    if(cn.length!=0){
		var l = bindElements(datas,ls[i]);
		for(j in l){
		    ret[j] = l[j]; // marge child nodes
		}
	    }
	}
    }
    return ret
}

function getNode(xml,name){
    for(var i = 0;i<xml.childNodes.length;i++){
	var tmp = xml.childNodes.item(i);
	if(tmp.tagName==name){
	    return tmp;
	}
    }
    return null;
}
function getAttr(xml,name){
   for(var i = 0;i<xml.attributes.length;i++){
	var tmp = xml.attributes.item(i);
	if(tmp.nodeName==name){
	    return tmp.nodeValue;
	}
    }
    return null;
}
function getList(xml,name){
    var ret = [];
   for(var i = 0;i<xml.childNodes.length;i++){
	var tmp = xml.childNodes.item(i);
	if(tmp.tagName==name){
	    ret.push(tmp);
	}
    }
    return ret;
}

var Record = function(name){
    var datas=["image_a","image","title","tags","other"];
    this.record=$("record_tmpl").cloneNode(true);
    ret = bindElements(datas,this.record);
    for(var x in ret){
	this[x] = ret[x];
    }
    var self = this;
    new Ajax.Request(name, {
	    method:'get',
	    parameters: '',
	    onComplete: function(ret){
		/*
		if(ret.status!=200){
		    //error
		    console.log("error"+ret.status);
		    return;
		    }*/
		var res = ret.responseXML;
		var doc = res.documentElement;
		var data = getNode(doc,"data");

		var tags = getNode(data,"tags");
		var tagl = getList(tags,"tag");
		self.image_a.href=getAttr(data,"url");
		var img_name = getAttr(data,"image");
		if(img_name==""){
		    self.image.src = "noimage.png";
		}else{
		    self.image.src = getAttr(data,"image");
		}
		self.title.innerHTML = 
		    "<h3><a href='"+getAttr(data,"url")+"'>"+
		    getAttr(data,"title")+
                    "<img src='ext.gif' border='0' />"+
		    "</a></h3>";
		self.other.innerHTML = "<a href='"+ name +"'>" + "PermaLink</a>";

		//Hatena.Star.EntryLoader.loadNewEntries(self.title);
		var s="";
		for(var i=0;i<tagl.length;i++){
		    s = document.createElement("span");
		    s.className="label label-info tag";
		    s.innerHTML=tagl[i].firstChild.nodeValue;
		    self.tags.appendChild(s);
		}

	    }});
}

var contents;
function init(){
    contents = $("contents");

   new Ajax.Request('data/files.json'+name, {
	    method:'post',
	    parameters: '',
	    onComplete:init_call});
}

function init_call(req){
    var files = eval(req.responseText);
    var r;
    for(var i=files.length-1;i>=0;i--){
	r = new Record(files[i]);
	contents.appendChild(r.record);
    }
}


