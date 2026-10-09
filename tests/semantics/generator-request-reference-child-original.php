<?php
class RequestRefPinPayload22{function __destruct(){echo "D";}}
class RequestRefPinLater22{function __destruct(){echo "Q";}}
class RequestRefPinLeaf22{function __destruct(){global $wg,$wp,$wb,$wl;echo "L",(int)($wb->get()===null),":",(int)($wl->get()!==null),":",(int)($wg->get()!==null),":",(int)($wp->get()!==null);throw new Exception("leaf");}}
class RequestRefPinParent22{public $leaf;}
class RequestRefPinException22 extends Exception{public $child;}
function requestRefPinHandler22($e){global $wb,$wl;echo "H";$x=new RequestRefPinException22("handler");$x->child=new RequestRefPinParent22;$leaf=new RequestRefPinLeaf22;$x->child->leaf=&$leaf;unset($leaf);$wb=WeakReference::create($x->child);$wl=WeakReference::create($x->child->leaf);throw $x;}
set_exception_handler("requestRefPinHandler22");
function requestRefPinGenerator22(){try{yield new RequestRefPinPayload22;}finally{echo "F";throw new Exception("new");}}
$wb=null;$keepBox=&$wb;$wl=null;$keepLeaf=&$wl;
$later=new RequestRefPinLater22;$g=requestRefPinGenerator22();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
