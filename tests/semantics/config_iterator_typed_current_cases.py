"""Typed-source capture, field rebinding and source retirement before CONFIG API."""

OWNED = b'''<?php
class TypedOwnedIterator67 implements Iterator {
    public int $pos=0;public ?string $name;public string $value;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $this->name;}
        return $this->value;
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {
            $GLOBALS["producer"]=null;$this->name="precision";
            echo "Q:",$GLOBALS["producerWatch"]->get()===null,";";
        } else {
            $GLOBALS["name"]="serialize_precision";
            try {$GLOBALS["held"]=[];}catch (TypeError $e) {echo "T;";}
            $this->value =& $GLOBALS["fresh"];$GLOBALS["held"]="17";
            echo "R:",$this->value,":",$GLOBALS["held"],";";
        }
        return $this->pos;
    }
    public function next():void {echo "N",$this->pos,";";$this->pos++;}
    public function __destruct() {
        echo "D:",ini_get("precision"),":",$this->name,":",$this->value,":",$GLOBALS["held"],";";
        unset($this->name);$GLOBALS["name"]=["free"];
        $GLOBALS["held"]=["old"];$GLOBALS["fresh"]=29;
        echo "M:",$GLOBALS["fresh"]==="29",":",$GLOBALS["name"][0],":",$GLOBALS["held"][0],";";
    }
}
class TypedOwnedAggregate67 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new TypedOwnedIterator67;
        $it->name =& $GLOBALS["name"];$it->value =& $GLOBALS["held"];
        $GLOBALS["watch"]=WeakReference::create($it);return $it;
    }
}
$name=null;$held="13";$fresh="23";$watch=null;$result=99;
$producer=new TypedOwnedAggregate67;$producerWatch=WeakReference::create($producer);
echo "B;";$result=ini_set(...$producer);
echo "A:",$result,":",ini_get("precision"),":",$name[0],":",$held[0],":",$fresh==="29",":",$watch->get()===null,":",$producerWatch->get()===null,";";
$fresh=["detached"];echo "F:",$fresh[0],";";
unset($name,$held,$fresh,$watch,$result,$producer,$producerWatch);
echo "U:",isset($name),":",isset($held),";";
'''

TEMPORARY = b'''<?php
class TypedOutsideSource67 {
    public string $name="precision";public string $value="13";
}
class TypedTemporaryIterator67 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";$owner=$GLOBALS["owner"];
        if ($this->pos===0) {return $owner->name;}
        return $owner->value;
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===1) {$owner=$GLOBALS["owner"];$owner->value=[];}
        return $this->pos;
    }
    public function next():void {echo "N",$this->pos,";";$this->pos++;}
}
function typedTemporaryIterator67() {
    echo "F;";$it=new TypedTemporaryIterator67;
    $GLOBALS["watch"]=WeakReference::create($it);return $it;
}
$owner=new TypedOutsideSource67;$held =& $owner->value;$watch=null;$result=99;
echo "B;";
try {$result=ini_set(...typedTemporaryIterator67());echo "BAD;";}
catch (TypeError $e) {
    echo "E:",$e->getPrevious()===null,":",$result,":",ini_get("precision"),":",$held,":",$watch->get()===null,";";
}
try {$held=[];}catch (TypeError $e) {echo "T;";}
unset($owner->value);$held=["free"];echo "F:",$held[0],";";
unset($e,$owner,$held,$watch,$result);echo "U:",isset($owner),":",isset($held),";";
'''

CASES = {
    'config-typed-current-owned-aggregate': OWNED,
    'config-typed-current-temporary-type-error': TEMPORARY,
}

EXPECTED = {
    'config-typed-current-owned-aggregate': b'B;G;W;V0;C0;K0;Q:1;N0;V1;C1;K1;T;R:23:17;N1;V2;D:14:serialize_precision:23:17;M:1:free:old;A:14:17:free:old:1:1:1;F:detached;U::;',
    'config-typed-current-temporary-type-error': b'B;F;W;V0;C0;K0;N0;V1;C1;K1;E:1:99:14:13:1;T;F:free;U::;',
}
