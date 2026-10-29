"""NULL option binding diagnoses only after scalar snapshots and DATA cleanup."""

BODY = b'''
class NullOptionIterator68 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $GLOBALS["value"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["producer"]=null;}
        else {$GLOBALS["value"]=17;}
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["name"]="precision";}
        else {$GLOBALS["value"]=29;}
        $this->pos++;
    }
    public function __destruct() {
        echo "D:",ini_get("precision"),":",$GLOBALS["name"],":",$GLOBALS["value"],";";
        ini_set("precision",19);$GLOBALS["value"]=31;
    }
}
class NullOptionAggregate68 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new NullOptionIterator68;
        $GLOBALS["watch"]=WeakReference::create($it);return $it;
    }
}
function nullOptionWarning68($severity,$message,$file,$line) {
    echo "H:",$severity===E_DEPRECATED,":",$GLOBALS["watch"]->get()===null,":",ini_get("precision"),":",$GLOBALS["result"],":",$GLOBALS["name"],":",$GLOBALS["value"],";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
    return true;
}
$name=null;$value=13;$producer=new NullOptionAggregate68;$watch=null;$result=99;
$saved=new Exception("null-option68");
'''

CALL = b'''set_error_handler("nullOptionWarning68");echo "B;";
try {
    $result=ini_set(...$producer);
    echo "R:",$result===false,":",ini_get("precision"),":",$watch->get()===null,":",$value,";";
} catch (Exception $e) {
    echo "E:",$e===$saved,":",$e->getPrevious()===null,":",$result,":",ini_get("precision"),":",$watch->get()===null,":",$value,";";
} catch (TypeError $e) {
    echo "T:",$e->getPrevious()===null,":",$result,":",ini_get("precision"),":",$watch->get()===null,":",$value,";";
}
restore_error_handler();unset($e,$name,$value,$producer,$watch,$result,$saved,$mode);
echo "U:",isset($name),":",isset($value),":",isset($watch),";";
'''

CASES = {
    'config-scalar-review-null-option-handler-return':
        b'<?php\n' + BODY + b'$mode="return";\n' + CALL,
    'config-scalar-review-null-option-handler-throw':
        b'<?php\n' + BODY + b'$mode="throw";\n' + CALL,
    'config-scalar-review-null-option-strict-type-error':
        b'<?php declare(strict_types=1);\n' + BODY + b'$mode="strict";\n' + CALL,
}

PREFIX = b'B;G;W;V0;C0;K0;N0;V1;C1;K1;N1;V2;D:14:precision:29;'
HANDLER = b'H:1:1:19:99:precision:31;'
EXPECTED = {
    'config-scalar-review-null-option-handler-return':
        PREFIX + HANDLER + b'R:1:19:1:31;U:::;',
    'config-scalar-review-null-option-handler-throw':
        PREFIX + HANDLER + b'E:1:1:99:19:1:31;U:::;',
    'config-scalar-review-null-option-strict-type-error':
        PREFIX + b'T:1:99:19:1:31;U:::;',
}
