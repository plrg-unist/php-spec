<?php
class RequestArrayPinPayload23{function __destruct(){echo "D";}}
class RequestArrayPinLater23{function __destruct(){echo "Q";}}
class RequestArrayPinLeaf23{function __destruct(){global $wg,$wp,$wb,$wl;echo "L",(int)($wb->get()===null),":",(int)($wl->get()!==null),":",(int)($wg->get()!==null),":",(int)($wp->get()!==null);throw new Exception("leaf");}}
class RequestArrayPinParent23{public $leaf;}
class RequestArrayPinException23 extends Exception{public $child;}
function requestArrayPinHandler23($e){global $wb,$wl,$holdArray;echo "H";$x=new RequestArrayPinException23("handler");$x->child=new RequestArrayPinParent23;$leaf=new RequestArrayPinLeaf23;$x->child->leaf=[$leaf];unset($leaf);$holdArray=$x->child->leaf;$wb=WeakReference::create($x->child);$wl=WeakReference::create($x->child->leaf[0]);throw $x;}
set_exception_handler("requestArrayPinHandler23");
function requestArrayPinGenerator23(){try{yield new RequestArrayPinPayload23;}finally{echo "F";throw new Exception("new");}}
$wb=null;$keepBox=&$wb;$wl=null;$keepLeaf=&$wl;
$later=new RequestArrayPinLater23;$g=requestArrayPinGenerator23();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
