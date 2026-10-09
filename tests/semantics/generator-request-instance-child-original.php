<?php
class RequestPinPayload21{function __destruct(){echo "D";}}
class RequestPinLater21{function __destruct(){echo "Q";}}
class RequestPinLeaf21{function __destruct(){global $wg,$wp,$wb,$wl;echo "L",(int)($wb->get()===null),":",(int)($wl->get()!==null),":",(int)($wg->get()!==null),":",(int)($wp->get()!==null);throw new Exception("leaf");}}
class RequestPinParent21{public $leaf;}
class RequestPinException21 extends Exception{public $child;}
function requestPinHandler21($e){global $wb,$wl;echo "H";$x=new RequestPinException21("handler");$x->child=new RequestPinParent21;$x->child->leaf=new RequestPinLeaf21;$wb=WeakReference::create($x->child);$wl=WeakReference::create($x->child->leaf);throw $x;}
set_exception_handler("requestPinHandler21");
function requestPinGenerator21(){try{yield new RequestPinPayload21;}finally{echo "F";throw new Exception("new");}}
$wb=null;$keepBox=&$wb;$wl=null;$keepLeaf=&$wl;
$later=new RequestPinLater21;$g=requestPinGenerator21();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
