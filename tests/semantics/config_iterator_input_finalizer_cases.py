"""Last temporary INPUT finalizes with distinct copied argument roots alive."""

OBJECT = b'''<?php
class InputPayload70 {
    public function __destruct() {
        echo "P:",(int)($GLOBALS["iteratorWatch"]->get()===null),":",$GLOBALS["stage"],";";
    }
}
class TemporaryInput70 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return "precision";}
        $payload=new InputPayload70;
        $GLOBALS["payloadWatch"]=WeakReference::create($payload);return $payload;
    }
    public function key():mixed {echo "K",$this->pos,";";return $this->pos;}
    public function next():void {echo "N",$this->pos,";";$this->pos++;}
    public function __destruct() {
        echo "I:",ini_get("precision"),":",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
        $GLOBALS["inputDtors"]++;ini_set("precision","7");
    }
}
function buildTemporaryInput70() {
    echo "F;";$it=new TemporaryInput70;
    $GLOBALS["iteratorWatch"]=WeakReference::create($it);return $it;
}
$iteratorWatch=null;$payloadWatch=null;$inputDtors=0;$result=99;$stage="walk";
echo "B;";
try {$result=ini_set(...buildTemporaryInput70());echo "BAD;";}
catch (TypeError $e) {
    echo "E:",(int)($e->getMessage()==='ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null'),":",$result,":",ini_get("precision"),":",(int)($iteratorWatch->get()===null),":",(int)($payloadWatch->get()!==null),":",$inputDtors,";";
    $trace=$e->getTrace();$arg=$trace[0]["args"][1];
    echo "T:",(int)($arg===$payloadWatch->get()),":",$inputDtors,";";
    unset($arg,$trace);$stage="release";unset($e);
    echo "R:",(int)($payloadWatch->get()===null),":",$inputDtors,";";
}
unset($iteratorWatch,$payloadWatch,$inputDtors,$result,$stage);
echo "U:",(int)isset($iteratorWatch),":",(int)isset($payloadWatch),";";
'''

ARRAY = b'''<?php
class TemporaryArrayInput70 implements Iterator {
    public int $pos=0;
    public array $row;
    public function __construct() {global $leaf;$this->row=[3,&$leaf];}
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {echo "C",$this->pos,";";return $this->pos===0?"precision":$this->row;}
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===1) {$this->row[0]=22;$GLOBALS["leaf"]=17;}
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===1) {$this->row[0]=33;$GLOBALS["leaf"]=29;}
        $this->pos++;
    }
    public function __destruct() {
        echo "I:",ini_get("precision"),":",$this->row[0],":",$this->row[1],";";
        $this->row[0]=44;$GLOBALS["leaf"]=31;$GLOBALS["inputDtors"]++;
        ini_set("precision","7");
    }
}
function buildTemporaryArrayInput70() {
    echo "F;";$it=new TemporaryArrayInput70;
    $GLOBALS["iteratorWatch"]=WeakReference::create($it);return $it;
}
$leaf=7;$iteratorWatch=null;$inputDtors=0;$result=99;echo "B;";
try {$result=ini_set(...buildTemporaryArrayInput70());echo "BAD;";}
catch (TypeError $e) {
    echo "E:",(int)($e->getMessage()==='ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null'),":",$result,":",ini_get("precision"),":",(int)($iteratorWatch->get()===null),":",$inputDtors,";";
    $trace=$e->getTrace();$captured=$trace[0]["args"][1];
    echo "T:",$trace[0]["args"][0],":",$captured[0],":",$captured[1],";";
    $leaf=66;$captured[0]=77;$captured[1]=88;$again=$e->getTrace();
    echo "V:",$again[0]["args"][1][0],":",$again[0]["args"][1][1],":",$captured[0],":",$captured[1],":",$leaf,";";
    unset($again,$captured,$trace,$e);
}
unset($leaf,$iteratorWatch,$inputDtors,$result);
echo "U:",(int)isset($leaf),":",(int)isset($iteratorWatch),";";
'''

CASES = {
    'config-temporary-input-object-argument-finalizer-trace': OBJECT,
    'config-temporary-input-declared-array-cow-finalizer': ARRAY,
}
WALK = b'B;F;W;V0;C0;K0;N0;V1;C1;K1;N1;V2;'
EXPECTED = {
    'config-temporary-input-object-argument-finalizer-trace': WALK +
        b'I:14:1;E:1:99:7:1:1:1;T:1:1;P:1:release;R:1:1;U:0:0;',
    'config-temporary-input-declared-array-cow-finalizer': WALK +
        b'I:14:33:29;E:1:99:7:1:1;T:precision:3:31;V:3:88:77:88:88;U:0:0;',
}
