"""An owning prefix survives COW and cache/DATA cleanup on a saved key throw."""

COMMON = b'''<?php
class PrefixPayload69 {
    public function __destruct() {
        echo "P:",(int)($GLOBALS["iteratorWatch"]->get()===null),":",(int)($GLOBALS["cacheWatch"]->get()===null),";";
    }
}
class CachePayload69 {
    public function __destruct() {
        echo "C:",(int)($GLOBALS["iteratorWatch"]->get()!==null),":",(int)($GLOBALS["prefixWatch"]->get()!==null),";";
    }
}
class BufferIterator69 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["prefix"];}
        return $GLOBALS["cache"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["producer"]=null;return 0;}
        unset($GLOBALS["cache"]);
        echo "Q1:",$GLOBALS["cacheWatch"]->get()!==null,";";
        throw $GLOBALS["saved"];
    }
    public function next():void {
        echo "N",$this->pos,";";
        $GLOBALS["prefix"][0]=7;
        echo "Q0:",$GLOBALS["prefixWatch"]->get()!==null,":",$GLOBALS["prefix"][0],";";
        unset($GLOBALS["prefix"]);$this->pos++;
    }
    public function __destruct() {
        echo "D:",(int)($GLOBALS["prefixWatch"]->get()!==null),":",(int)($GLOBALS["cacheWatch"]->get()!==null),";";
    }
}
class BufferAggregate69 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new BufferIterator69;
        $GLOBALS["iteratorWatch"]=WeakReference::create($it);return $it;
    }
}
$prefix=[new PrefixPayload69];$cache=new CachePayload69;
$prefixWatch=WeakReference::create($prefix[0]);$cacheWatch=WeakReference::create($cache);
$iteratorWatch=null;$producer=new BufferAggregate69;$result=99;
$saved=new Exception("buffer-peer69");
'''

CALL = b'''if ($mode==="held") {$held =& $cache;}
echo "B;";
try {$result=ini_set(...$producer);echo "BAD;";}
catch (Exception $e) {
    echo "E:",$e===$saved,":",$e->getPrevious()===null,":",$result,":",(int)($iteratorWatch->get()===null),":",(int)($prefixWatch->get()===null),":",(int)($cacheWatch->get()===null),";";
}
if ($mode==="held") {echo "H;";unset($held);}
echo "A:",$cacheWatch->get()===null,";";
unset($e,$saved,$prefix,$cache,$producer,$result,$mode,$iteratorWatch,$prefixWatch,$cacheWatch);
echo "U:",isset($prefix),":",isset($cache),":",isset($held),";";
'''

NAMED_COMMON = COMMON.replace(b'throw $GLOBALS["saved"];', b'return "unknown69";')
NAMED_CALL = CALL.replace(b'catch (Exception $e)', b'catch (Throwable $e)').replace(
    b'$e===$saved,":",$e->getPrevious()===null',
    b"$e instanceof Error,\":\",$e->getMessage()==='Unknown named parameter $unknown69',\":\",$e->getPrevious()===null")

CASES = {
    'config-argument-review-prefix-cow-key-throw':
        COMMON + b'$mode="sole";\n' + CALL,
    'config-argument-review-prefix-cow-retained-cache':
        COMMON + b'$mode="held";\n' + CALL,
    'config-argument-review-prefix-cow-unknown-name':
        NAMED_COMMON + b'$mode="sole";\n' + NAMED_CALL,
}

PREFIX = b'B;G;W;V0;C0;K0;N0;Q0:1:7;V1;C1;K1;Q1:1;'
EXPECTED = {
    'config-argument-review-prefix-cow-key-throw':
        PREFIX + b'C:1:1;D:1:0;P:1:1;E:1:1:99:1:1:1;A:1;U:::;',
    'config-argument-review-prefix-cow-retained-cache':
        PREFIX + b'D:1:1;P:1:0;E:1:1:99:1:1:0;H;C:0:0;A:1;U:::;',
    'config-argument-review-prefix-cow-unknown-name':
        PREFIX + b'C:1:1;D:1:0;P:1:1;E:1:1:1:99:1:1:1;A:1;U:::;',
}
