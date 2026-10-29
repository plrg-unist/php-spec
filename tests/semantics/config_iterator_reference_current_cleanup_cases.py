"""Last current-cell owner retires its payload before CONFIG DATA/INPUT."""

CASES = {
    'config-reference-current-cache-only-throw': b'''<?php
class CacheOnlyPayload66 {
    public function __destruct() {
        $GLOBALS["stamp"]=1;
        echo "X:",$GLOBALS["watch"]->get()!==null,":",ini_get("precision"),":",isset($GLOBALS["slot"]),";";
    }
}
class CacheOnlyIterator66 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<1;}
    public function &current():mixed {echo "C;";return $GLOBALS["slot"];}
    public function key():mixed {
        echo "K;";unset($GLOBALS["slot"]);
        echo "Q:",$GLOBALS["stamp"],":",$GLOBALS["watch"]->get()!==null,":",isset($GLOBALS["slot"]),";";
        throw $GLOBALS["saved"];
    }
    public function next():void {echo "N;";$this->pos++;}
}
function cacheOnlyIterator66() {
    echo "F;";$it=new CacheOnlyIterator66;
    $GLOBALS["watch"]=WeakReference::create($it);return $it;
}
$saved=new Exception("cache-only66");$slot=new CacheOnlyPayload66;
$stamp=0;$watch=null;$result=99;echo "B;";
try {$result=ini_set(...cacheOnlyIterator66());echo "BAD;";}
catch (Exception $e) {
    echo "E:",$e===$saved,":",$e->getPrevious()===null,":",$result,":",ini_get("precision"),":",$stamp,":",$watch->get()===null,":",isset($slot),";";
}
unset($e,$saved,$result,$watch,$stamp,$slot);echo "U:",isset($slot),":",isset($watch),";";
''',
}

EXPECTED = {
    'config-reference-current-cache-only-throw': b'B;F;W;V0;C;K;Q:0:1:;X:1:14:;E:1:1:99:14:1:1:;U::;',
}
