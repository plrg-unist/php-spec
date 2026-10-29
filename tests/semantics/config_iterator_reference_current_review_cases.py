"""Independent selected-cell identity and copied CONFIG argument snapshots."""

COMMON = br'''<?php
class SelectedCellSnapshot66 implements Iterator {
    public $name;public $value;public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<2;}
    public function &current():mixed {
        echo "C",$this->position,";";
        if ($this->position===0) {return $this->name;}
        return $this->value;
    }
    public function key():mixed {
        echo "K",$this->position,";";
        if ($this->position===0) {
            $this->name="precision";$GLOBALS["producer"]=null;
            echo "A:",$GLOBALS["producerWatch"]->get()===null,";";
            return 0;
        }
        $GLOBALS["nameRef"]="serialize_precision";
        $this->value =& $GLOBALS["fresh"];
        $GLOBALS["held"]="17";
        echo "Q:",$this->value,":",$GLOBALS["held"],";";
        if ($GLOBALS["throwKey"]) {throw $GLOBALS["saved"];}
        return 1;
    }
    public function next():void {echo "N;";++$this->position;}
    public function __destruct() {
        echo "D:",ini_get("precision"),":",$this->name,":",$this->value,":",$GLOBALS["held"],":",$GLOBALS["watch"]->get()===$this,";";
        $GLOBALS["held"]="19";$GLOBALS["fresh"]="29";
        echo "M:",$GLOBALS["held"],":",$GLOBALS["fresh"],";";
    }
}
class SelectedCellAggregate66 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new SelectedCellSnapshot66;
        $it->name =& $GLOBALS["nameRef"];$it->value =& $GLOBALS["held"];
        $GLOBALS["watch"]=WeakReference::create($it);
        return $it;
    }
}
$nameRef="bogus";$held="3";$fresh="23";$watch=null;$result=99;
$producer=new SelectedCellAggregate66;$producerWatch=WeakReference::create($producer);
echo "P:",ini_get("precision"),";";
'''

CLEANUP = br'''unset($e,$saved,$result,$nameRef,$held,$fresh,$watch,$producer,$producerWatch,$throwKey);
echo "U:",isset($producer),":",isset($held),":",isset($fresh),";";
'''

CASES = {
    'config-iterator-reference-current-review-selected-cell-snapshot': COMMON + br'''$throwKey=false;$saved=null;
$result=ini_set(...$producer);
echo "R:",$result,":",ini_get("precision"),":",$nameRef,":",$held,":",$fresh,":",$watch->get()===null,":",$producerWatch->get()===null,";";
''' + CLEANUP,
    'config-iterator-reference-current-review-selected-cell-throw': COMMON + br'''$throwKey=true;$saved=new Exception("peer66");
try {$result=ini_set(...$producer);echo "BAD;";}
catch (Exception $e) {
    echo "E:",$e===$saved,":",$e->getPrevious()===null,":",$result,":",ini_get("precision"),":",$nameRef,":",$held,":",$fresh,":",$watch->get()===null,":",$producerWatch->get()===null,";";
}
''' + CLEANUP,
}

EXPECTED = {
    'config-iterator-reference-current-review-selected-cell-snapshot': b'P:14;G;W;V0;C0;K0;A:1;N;V1;C1;K1;Q:23:17;N;V2;D:14:serialize_precision:23:17:1;M:19:29;R:14:17:serialize_precision:19:29:1:1;U:::;',
    'config-iterator-reference-current-review-selected-cell-throw': b'P:14;G;W;V0;C0;K0;A:1;N;V1;C1;K1;Q:23:17;D:14:serialize_precision:23:17:1;M:19:29;E:1:1:99:14:serialize_precision:19:29:1:1;U:::;',
}
