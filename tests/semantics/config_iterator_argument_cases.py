"""Owning Iterator arguments preserve COW snapshots and API TraceArgs lifetime."""

ARRAY_BODY = b'''<?php
class ArrayArgumentIterator69 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $GLOBALS["row"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["producer"]=null;}
        else {
            $GLOBALS["name"]="other";$GLOBALS["row"][0]=22;
            $GLOBALS["leaf"]=17;unset($GLOBALS["saved"]);
        }
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===1) {
            $GLOBALS["row"][0]=33;$GLOBALS["row"][1]=29;
            unset($GLOBALS["leaf"]);
        }
        $this->pos++;
    }
    public function __destruct() {
        echo "D:",ini_get("precision"),":",$GLOBALS["row"][0],":",$GLOBALS["row"][1],";";
        $GLOBALS["row"][0]=44;$GLOBALS["row"][1]=31;
    }
}
class ArrayArgumentAggregate69 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new ArrayArgumentIterator69;
        $GLOBALS["watch"]=WeakReference::create($it);return $it;
    }
}
$name="precision";$leaf=7;$row=[3,&$leaf];$saved=$row;
$producer=new ArrayArgumentAggregate69;$watch=null;$result=99;echo "B;";
try {$result=ini_set(...$producer);echo "BAD;";}
catch (TypeError $e) {
    echo "E:",$e->getMessage()==='ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null',":",$result,":",ini_get("precision"),":",$row[0],":",$row[1],":",$watch->get()===null,";";
    $trace=$e->getTrace();$captured=$trace[0]["args"][1];
    echo "T:",$trace[0]["args"][0],":",$captured[0],":",$captured[1],";";
    $row[0]=55;$row[1]=66;
    echo "F:",$captured[0],":",$captured[1],":",$row[0],":",$row[1],";";
    $captured[0]=77;$captured[1]=88;$again=$e->getTrace();
    echo "V:",$again[0]["args"][1][0],":",$again[0]["args"][1][1],":",$captured[0],":",$captured[1],":",$row[0],":",$row[1],";";
    unset($again,$captured,$trace,$e);
}
unset($name,$leaf,$row,$saved,$producer,$watch,$result);echo "U:",isset($row),":",isset($watch),";";
'''

REFERENCE_ARRAY = ARRAY_BODY.replace(b'public function current():mixed',
    b'public function &current():mixed').replace(b'ArrayArgument', b'ReferenceArrayArgument')

SELF_OBJECT = b'''<?php
class SelfArgumentIterator69 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {echo "C",$this->pos,";";return $this->pos===0?"precision":$this;}
    public function key():mixed {echo "K",$this->pos,";";if ($this->pos===0) {$GLOBALS["producer"]=null;}return $this->pos;}
    public function next():void {echo "N",$this->pos,";";$this->pos++;}
    public function __destruct() {echo "D:",ini_get("precision"),":",$GLOBALS["stage"],";";$GLOBALS["dtors"]++;}
}
class SelfArgumentAggregate69 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new SelfArgumentIterator69;
        $GLOBALS["watch"]=WeakReference::create($it);return $it;
    }
}
$producer=new SelfArgumentAggregate69;$watch=null;$result=99;$dtors=0;$stage="walk";
echo "B;";
try {$result=ini_set(...$producer);echo "BAD;";}
catch (TypeError $e) {
    echo "E:",$e->getMessage()==='ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null',":",$result,":",ini_get("precision"),":",$watch->get()!==null,":",$dtors,";";
    $trace=$e->getTrace();$arg=$trace[0]["args"][1];
    echo "T:",$arg===$watch->get(),":",$arg->pos,":",$dtors,";";
    unset($arg,$trace);$stage="release";unset($e);
    echo "R:",$watch->get()===null,":",$dtors,";";
}
unset($producer,$watch,$result,$dtors,$stage);echo "U:",isset($producer),":",isset($watch),";";
'''

CASES = {
    'config-owning-argument-byval-array-api-trace': ARRAY_BODY,
    'config-owning-argument-byref-array-api-trace': REFERENCE_ARRAY,
    'config-owning-argument-self-object-api-trace': SELF_OBJECT,
}
WALK = b'B;G;W;V0;C0;K0;N0;V1;C1;K1;N1;V2;'
EXPECTED = {
    'config-owning-argument-byval-array-api-trace': WALK +
        b'D:14:33:29;E:1:99:14:44:31:1;T:precision:3:31;F:3:66:55:66;V:3:88:77:88:55:88;U::;',
    'config-owning-argument-byref-array-api-trace': WALK +
        b'D:14:33:29;E:1:99:14:44:31:1;T:precision:22:31;F:22:66:55:66;V:22:88:77:88:55:88;U::;',
    'config-owning-argument-self-object-api-trace': WALK +
        b'E:1:99:14:1:0;T:1:2:0;D:14:release;R:1:1;U::;',
}
