"""Invalid-key cleanup must retire CURRENT before DATA and the builder after it."""

CASES = {
    'array-iterator-fields-invalid-scalar-cleanup-order': b'''<?php
class ScalarCleanupOrder implements Iterator {
    public $cache;public $prefix;public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {return $this->position<1;}
    public function &current():mixed {echo "C;";return $this->cache[0];}
    public function key():mixed {$GLOBALS["savedCache"]=$this->cache;unset($GLOBALS["prefixLeaf"]);echo "K;";return false;}
    public function next():void {$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["savedCache"][0],":",$GLOBALS["savedPrefix"][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,";";
        $this->cache[0]=44;$this->prefix[0]=55;
        echo "M:",$this->cache[0],":",$this->prefix[0],":",$GLOBALS["savedCache"][0],":",$GLOBALS["savedPrefix"][0],";";
    }
}
$cacheLeaf=2;$prefixLeaf=3;$dest=99;
$it=new ScalarCleanupOrder;$it->cache=[&$cacheLeaf];$it->prefix=[&$prefixLeaf];
$savedCache=[2];$savedPrefix=$it->prefix;unset($cacheLeaf);
$watch=WeakReference::create($it);echo "P:",$watch->get()===$it,";";
try {$dest=[&$prefixLeaf,...$it];echo "L;";}
catch (Error $e) {
    echo "E:",$e->getMessage()==="Keys must be of type int|string during array unpacking",":",$e->getPrevious()===null,":",$savedCache[0],":",$savedPrefix[0],":",$dest===99,":",$watch->get()===null,":",isset($prefixLeaf),";";
}
unset($e,$savedCache,$savedPrefix,$dest,$watch);
echo "U:",isset($it),":",isset($savedCache),":",isset($savedPrefix),";";
''',
}

EXPECTED = {
    'array-iterator-fields-invalid-scalar-cleanup-order': b'P:1;C;K;D:2:3:1:1;M:44:55:2:55;E:1:1:2:55:1:1:;U:::;',
}
