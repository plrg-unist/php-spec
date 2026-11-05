"""Normal Stringable option copies outlive ordinary Iterator traversal."""

DATA_RELEASE = b'''<?php
class ReviewOption98 {
    public function __toString():string {
        $GLOBALS["casts"]++;
        echo "S:",$GLOBALS["iteratorWatch"]->get()===null,":",ini_get("precision"),";";
        return "precision";
    }
    public function __destruct() {
        echo "O:",ini_get("precision"),":",$GLOBALS["casts"],";";
        ini_set("precision","23");
    }
}
class ReviewIterator98 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $GLOBALS["value"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["producer"]=null;}
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===0) {unset($GLOBALS["name"]);}
        else {$GLOBALS["value"]=31;}
        $this->pos++;
    }
    public function __destruct() {
        echo "D:",$GLOBALS["casts"],":",ini_get("precision"),":",$GLOBALS["optionWatch"]->get()!==null,";";
        ini_set("precision","19");
    }
}
class ReviewAggregate98 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new ReviewIterator98;
        $GLOBALS["iteratorWatch"]=WeakReference::create($it);return $it;
    }
}
$name=new ReviewOption98;$value=7;$casts=0;$producer=new ReviewAggregate98;
$optionWatch=WeakReference::create($name);$iteratorWatch=null;
echo "B;";$result=ini_set(...$producer);
echo "A:",$result,":",ini_get("precision"),":",$casts,":",$value,":",$optionWatch->get()===null,":",$iteratorWatch->get()===null,";";
unset($producer,$optionWatch,$iteratorWatch,$value,$casts,$result);echo "U:",isset($name),":",isset($producer),";";
'''

RETAINED_NAMED = b'''<?php
class RetainedReviewOption98 {
    public function __toString():string {
        $GLOBALS["casts"]++;
        echo "S:",$GLOBALS["iteratorWatch"]->get()!==null,":",ini_get("precision"),";";
        ini_set("precision","17");return "precision";
    }
    public function __destruct() {echo "O:",ini_get("precision"),":",$GLOBALS["casts"],";";}
}
class RetainedReviewIterator98 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $GLOBALS["value"];
    }
    public function key():mixed {echo "K",$this->pos,";";return $this->pos===0?"option":"value";}
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["name"]="replacement";}
        else {$GLOBALS["value"]=47;}
        $this->pos++;
    }
    public function __destruct() {echo "D:",ini_get("precision"),";";}
}
$name=new RetainedReviewOption98;$hold=$name;$value=13;$casts=0;
$it=new RetainedReviewIterator98;$iteratorWatch=WeakReference::create($it);$optionWatch=WeakReference::create($name);
echo "B;";$result=ini_set(...$it);
echo "A:",$result,":",ini_get("precision"),":",$casts,":",$value,":",$name==="replacement",":",$optionWatch->get()===$hold,":",$iteratorWatch->get()===$it,";";
unset($hold);echo "R:",$optionWatch->get()===null,";";unset($it);
unset($name,$value,$casts,$result,$iteratorWatch,$optionWatch);echo "U:",isset($hold),":",isset($it),";";
'''

REFERENCE_KEY = b'''<?php
class ReferenceReviewOption98 {
    public function __toString():string {
        $GLOBALS["casts"]++;
        echo "S:",$GLOBALS["iteratorWatch"]->get()===null,":",ini_get("precision"),";";
        return "precision";
    }
    public function __destruct() {echo "O:",ini_get("precision"),";";ini_set("precision","27");}
}
class ReferenceReviewIterator98 implements Iterator {
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
        if ($this->pos===0) {$GLOBALS["name"]=$GLOBALS["selected"];unset($GLOBALS["selected"]);}
        else {$GLOBALS["value"]=9;$GLOBALS["it"]=null;}
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["name"]="later";}
        else {$GLOBALS["value"]=33;}
        $this->pos++;
    }
    public function __destruct() {echo "D:",$GLOBALS["casts"],";";ini_set("precision","21");}
}
$name="initial";$selected=new ReferenceReviewOption98;$value=5;$casts=0;$it=new ReferenceReviewIterator98;
$iteratorWatch=WeakReference::create($it);$optionWatch=WeakReference::create($selected);
echo "B;";$result=ini_set(...$it);
echo "A:",$result,":",ini_get("precision"),":",$casts,":",$value,":",$name==="later",":",$optionWatch->get()===null,":",$iteratorWatch->get()===null,";";
unset($name,$value,$casts,$it,$result,$iteratorWatch,$optionWatch);echo "U:",isset($selected),":",isset($it),";";
'''

CASES = {
    'config-stringable-name-review-data-release': DATA_RELEASE,
    'config-stringable-name-review-retained-named': RETAINED_NAMED,
    'config-stringable-name-review-reference-key': REFERENCE_KEY,
}
WALK = b'W;V0;C0;K0;N0;V1;C1;K1;N1;V2;'
EXPECTED = {
    'config-stringable-name-review-data-release': b'B;G;'+WALK+b'D:0:14:1;S:1:19;O:19:1;A:23:7:1:31:1:1;U::;',
    'config-stringable-name-review-retained-named': b'B;'+WALK+b'S:1:14;A:17:13:1:47:1:1:1;O:13:1;R:1;D:13;U::;',
    'config-stringable-name-review-reference-key': b'B;'+WALK+b'D:0;S:1:21;O:21;A:27:9:1:33:1:1:1;U::;',
}
