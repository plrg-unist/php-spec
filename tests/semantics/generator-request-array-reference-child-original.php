<?php
class RequestArrayRefPinPayload24{function __destruct(){echo "D";}}
class RequestArrayRefPinLater24{function __destruct(){echo "Q";}}
class RequestArrayRefPinLeaf24{function __destruct(){global $wg,$wp,$wb,$wl;echo "L",(int)($wb->get()===null),":",(int)($wl->get()!==null),":",(int)($wg->get()!==null),":",(int)($wp->get()!==null);throw new Exception("leaf");}}
class RequestArrayRefPinParent24{public $leaf;}
class RequestArrayRefPinException24 extends Exception{public $child;}
function requestArrayRefPinHandler24($e){global $wb,$wl;echo "H";$x=new RequestArrayRefPinException24("handler");$x->child=new RequestArrayRefPinParent24;$leaf=new RequestArrayRefPinLeaf24;$x->child->leaf=[&$leaf];unset($leaf);$wb=WeakReference::create($x->child);$wl=WeakReference::create($x->child->leaf[0]);throw $x;}
set_exception_handler("requestArrayRefPinHandler24");
function requestArrayRefPinGenerator24(){try{yield new RequestArrayRefPinPayload24;}finally{echo "F";throw new Exception("new");}}
$wb=null;$keepBox=&$wb;$wl=null;$keepLeaf=&$wl;
$later=new RequestArrayRefPinLater24;$g=requestArrayRefPinGenerator24();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
