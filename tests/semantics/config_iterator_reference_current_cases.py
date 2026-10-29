"""Selected CONFIG reference cells survive key writes and source-name rebinding."""

SELECTED = b'''<?php
class ConfigSelectedCell66 implements Iterator {
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
        if ($this->pos===0) {
            $GLOBALS["it"]=99;$GLOBALS["call"]=ini_get(...);
            $GLOBALS["name"]="precision";
        } else {
            $GLOBALS["name"]="serialize_precision";
            $GLOBALS["value"]=&$GLOBALS["fresh"];
            $GLOBALS["held"]="17";
        }
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===1) {$GLOBALS["held"]="19";$GLOBALS["fresh"]="29";}
        $this->pos++;
    }
}
$name=0;$value="13";$held=&$value;$fresh="23";
$it=new ConfigSelectedCell66;$keep=$it;$call=ini_set(...);$keepCall=$call;$result=99;
echo "B;";$result=$call(...$it);
echo "A:",$result,":",ini_get("precision"),":",$held,":",$value,":",$fresh,":",$name,":",$it,":",$keep->pos,":",$call("precision"),";";
echo "F:",$keepCall("precision","12"),":",ini_get("precision"),";";
unset($it,$keep,$call,$keepCall,$name,$value,$held,$fresh,$result);
echo "U:",isset($it),":",isset($value),":",isset($held),";";
'''

TEMPORARY = b'''<?php
class ConfigReferenceTemporary66 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {echo "C",$this->pos,";";return $GLOBALS["slot"];}
    public function key():mixed {
        echo "K",$this->pos,";";
        $GLOBALS["slot"]=$this->pos===0?"precision":"21";
        echo "Q",$this->pos,";";
        return $this->pos;
    }
    public function next():void {echo "N",$this->pos,";";if ($this->pos===1) {$GLOBALS["slot"]="23";}$this->pos++;}
}
function configReferenceTemporary66() {
    echo "F;";$it=new ConfigReferenceTemporary66;
    $GLOBALS["watch"]=WeakReference::create($it);return $it;
}
$slot=0;$watch=null;$result=99;echo "B;";
$result=ini_set(...configReferenceTemporary66());
echo "A:",$result,":",ini_get("precision"),":",$slot,":",$watch->get()===null,";";
unset($slot,$watch,$result);echo "U:",isset($slot),":",isset($watch),";";
'''

PAYLOAD = TEMPORARY.replace(b'<?php\n', b'''<?php
class ConfigCurrentPayload66 {
    public function __destruct() {echo "X:",ini_get("precision"),";";}
}
''', 1).replace(b'$slot=0;', b'$slot=new ConfigCurrentPayload66;', 1)

TYPED = b'''<?php
class ConfigTypedCurrent66 implements Iterator {
    public int $pos=0;
    public string $value="13";
    public function rewind():void {$this->pos=0;}
    public function valid():bool {return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $this->value;
    }
    public function key():mixed {echo "K",$this->pos,";";if ($this->pos===0) {$GLOBALS["name"]="precision";}else{$this->value="17";}return $this->pos;}
    public function next():void {$this->pos++;}
}
$name=0;$it=new ConfigTypedCurrent66;$result=99;echo "B;";
$result=ini_set(...$it);echo "A:",$result,":",ini_get("precision"),":",$it->value,";";
unset($it,$name,$result);echo "U:",isset($it),":",isset($name),";";
'''

CASES = {
    'config-reference-current-selected-global-cells': SELECTED,
    'config-reference-current-temporary': TEMPORARY,
    'config-reference-current-owning-value-repair': PAYLOAD,
    'config-reference-current-post-key-integer-boundary': SELECTED.replace(
        b'$GLOBALS["held"]="17";', b'$GLOBALS["held"]=17;', 1),
    'config-reference-current-typed-cell-boundary': TYPED,
}

EXPECTED = {
    'config-reference-current-selected-global-cells': b'B;W;V0;C0;K0;N0;V1;C1;K1;N1;V2;A:14:17:19:29:29:serialize_precision:99:2:17;F:17:12;U:::;',
    'config-reference-current-temporary': b'B;F;W;V0;C0;K0;Q0;N0;V1;C1;K1;Q1;N1;V2;A:14:21:23:1;U::;',
    'config-reference-current-owning-value-repair': b'B;F;W;V0;C0;K0;X:14;Q0;N0;V1;C1;K1;Q1;N1;V2;A:14:21:23:1;U::;',
    'config-reference-current-post-key-integer-boundary': b'B;W;V0;C0;K0;N0;V1;C1;K1;N1;V2;A:14:17:19:29:29:serialize_precision:99:2:17;F:17:12;U:::;',
    'config-reference-current-typed-cell-boundary': b'B;C0;K0;C1;K1;A:14:17:17;U::;',
}

BOUNDARIES = {
}
