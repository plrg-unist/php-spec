"""Instance/static type-source lifetimes across a selected CONFIG cell."""

COMMON = br'''<?php
class InstanceSource67 {public string $value="13";}
class StaticSource67 {public static string $slot="13";}
class SourceSelection67 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $GLOBALS["held"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {return 0;}
        try {$GLOBALS["old"]=[];}catch (TypeError $e) {echo "X:",$GLOBALS["old"],";";}
        unset($GLOBALS["first"]->value);
        try {$GLOBALS["old"]=[];}catch (TypeError $e) {echo "Y:",$GLOBALS["old"],";";}
        $GLOBALS["held"] =& $GLOBALS["fresh"];
        $GLOBALS["old"]="17";
        echo "Q:",$GLOBALS["old"],":",$GLOBALS["held"],":",StaticSource67::$slot,";";
        if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
        return 1;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===1) {
            StaticSource67::$slot =& $GLOBALS["fresh"];
            $GLOBALS["old"]=[$GLOBALS["stamp"]];
            try {$GLOBALS["fresh"]=[];}catch (TypeError $e) {echo "Z:",$GLOBALS["fresh"],";";}
        }
        $this->pos++;
    }
}
$name="precision";$fresh="23";$stamp="after";$first=new InstanceSource67;
$held =& $first->value;$old =& $held;StaticSource67::$slot =& $held;
$it=new SourceSelection67;$result=99;echo "B;";
'''

CLEANUP = br'''$reset="5";StaticSource67::$slot =& $reset;
unset($e,$t,$saved,$it,$first,$held,$old,$fresh,$name,$mode,$result,$stamp,$reset);
echo "U:",isset($held),":",isset($old),":",isset($fresh),";";
'''

CASES = {
    'config-typed-current-review-instance-static-detach-snapshot': COMMON + br'''$mode="normal";$saved=null;
$result=ini_set(...$it);
echo "A:",$result,":",ini_get("precision"),":",$old[0],":",$held,":",StaticSource67::$slot,":",(int)isset($first->value),";";
''' + CLEANUP,
    'config-typed-current-review-instance-static-detach-throw': COMMON + br'''$mode="throw";$saved=new Exception("peer67");
try {$result=ini_set(...$it);echo "BAD;";}
catch (Exception $e) {
    echo "E:",$e===$saved,":",$e->getPrevious()===null,":",$result,":",ini_get("precision"),":",$old,":",$held,":",StaticSource67::$slot,":",$it->pos,";";
    try {$old=[];}catch (TypeError $t) {echo "T:",$old,";";}
    StaticSource67::$slot =& $fresh;$stamp="caught";$old=[$stamp];
    echo "D:",$old[0],":",$held,":",StaticSource67::$slot,";";
}
''' + CLEANUP,
}

EXPECTED = {
    'config-typed-current-review-instance-static-detach-snapshot': b'B;W;V0;C0;K0;N0;V1;C1;K1;X:13;Y:13;Q:17:23:17;N1;Z:23;V2;A:14:17:after:23:23:0;U:::;',
    'config-typed-current-review-instance-static-detach-throw': b'B;W;V0;C0;K0;N0;V1;C1;K1;X:13;Y:13;Q:17:23:17;E:1:1:99:14:17:23:17:1;T:17;D:caught:23:23;U:::;',
}
