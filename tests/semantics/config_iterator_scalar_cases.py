"""Raw scalar Iterator sends defer INI_SET binding and conversion until API entry."""

VALUE_MATRIX = b'''<?php declare(strict_types=1);
class ScalarValueIterator68 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["option"];}
        return $GLOBALS["value"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["option"]="other";}
        else {$GLOBALS["value"]="later";}
        return $this->pos;
    }
    public function next():void {echo "N",$this->pos,";";$this->pos++;}
}
$values=[null,false,true,17,17.5];
foreach ($values as $index=>$entry) {
    $option="precision";$value=$entry;$it=new ScalarValueIterator68;$result=99;
    echo "B",$index,";";$result=ini_set(...$it);
    echo "A:",$result,":",ini_get("precision"),":",$option==="other",":",$value==="later",";";
    ini_set("precision","14");unset($it,$option,$value,$result);
}
unset($values,$index,$entry);echo "U:",isset($it),":",isset($value),";";
'''

OPTION_MATRIX = b'''<?php
class ScalarOptionIterator68 implements Iterator {
    public int $pos=0;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["option"];}
        return $GLOBALS["value"];
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["option"]="precision";}
        else {$GLOBALS["value"]=29;}
        return $this->pos;
    }
    public function next():void {echo "N",$this->pos,";";$this->pos++;}
}
$options=[true,17,1.25];
foreach ($options as $index=>$entry) {
    $option=$entry;$value=13;$it=new ScalarOptionIterator68;$result=99;
    echo "B",$index,";";$result=ini_set(...$it);
    echo "A:",$result===false,":",ini_get("precision"),":",$option==="precision",":",$value===29,";";
    unset($it,$option,$value,$result);
}
unset($options,$index,$entry);echo "U:",isset($it),":",isset($value),";";
'''

STRICT_INVOKE = OPTION_MATRIX[:OPTION_MATRIX.index(b'$options=')].replace(
    b'<?php\n', b'<?php declare(strict_types=1);\n', 1).replace(
    b'ScalarOptionIterator68', b'StrictScalarOptionIterator68') + b'''
$setter=ini_set(...);$option=17.25;$value=13;$it=new StrictScalarOptionIterator68;$result=99;
echo "S;";
try {$result=$setter(...$it);echo "BAD;";}
catch (TypeError $e) {
    echo "T:",$e->getMessage()==="ini_set(): Argument #1 ($option) must be of type string, float given",":",$result,":",ini_get("precision"),":",$option,":",$value,";";
}
unset($it,$e);$option=17.25;$value=13;$it=new StrictScalarOptionIterator68;$result=99;
echo "I;";$result=$setter->__invoke(...$it);
echo "R:",$result===false,":",ini_get("precision"),":",$option,":",$value,";";
unset($it,$setter,$option,$value,$result);echo "U:",isset($it),":",isset($value),";";
'''

FLOAT_API = b'''<?php
class ScalarFloatIterator68 implements Iterator {
    public int $pos=0;
    public float $value=1.5;
    public function rewind():void {echo "W;";$this->pos=0;}
    public function valid():bool {echo "V",$this->pos,";";return $this->pos<2;}
    public function &current():mixed {
        echo "C",$this->pos,";";
        if ($this->pos===0) {return $GLOBALS["name"];}
        return $this->value;
    }
    public function key():mixed {
        echo "K",$this->pos,";";
        if ($this->pos===0) {$GLOBALS["producer"]=99;}
        else {
            $GLOBALS["name"]="other";$this->value=&$GLOBALS["fresh"];
            $GLOBALS["held"]=1.2345678901234567;
        }
        return $this->pos;
    }
    public function next():void {
        echo "N",$this->pos,";";
        if ($this->pos===1) {$GLOBALS["held"]=2.5;$GLOBALS["fresh"]=3.5;}
        $this->pos++;
    }
    public function __destruct() {
        echo "D:",ini_get("precision"),";";ini_set("precision","3");
        $GLOBALS["held"]=4.5;$GLOBALS["fresh"]=6.5;
        echo "M:",ini_get("precision"),";";
    }
}
class ScalarFloatAggregate68 implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";$it=new ScalarFloatIterator68;
        $GLOBALS["held"]=&$it->value;
        $GLOBALS["watch"]=WeakReference::create($it);return $it;
    }
}
$name="precision";$held=null;$fresh=9.5;$producer=new ScalarFloatAggregate68;$watch=null;$result=99;
echo "B;";$result=ini_set(...$producer);
echo "A:",$result,":",ini_get("precision"),":",$held===4.5,":",$fresh===6.5,":",$watch->get()===null,";";
$fresh=false;echo "F:",$fresh===false,";";
unset($name,$held,$fresh,$producer,$watch,$result);echo "U:",isset($held),":",isset($fresh),";";
'''

CASES = {
    'config-scalar-current-strict-value-matrix': VALUE_MATRIX,
    'config-scalar-current-weak-option-matrix': OPTION_MATRIX,
    'config-scalar-current-strict-option-explicit-invoke': STRICT_INVOKE,
    'config-scalar-current-float-api-after-data-destructor': FLOAT_API,
}

WALK = b'W;V0;C0;K0;N0;V1;C1;K1;N1;V2;'
EXPECTED = {
    'config-scalar-current-strict-value-matrix':
        b''.join(b'B'+str(i).encode()+b';'+WALK+b'A:14:'+v+b':1:1;'
                 for i,v in enumerate([b'',b'',b'1',b'17',b'17.5']))+b'U::;',
    'config-scalar-current-weak-option-matrix':
        b''.join(b'B'+str(i).encode()+b';'+WALK+b'A:1:14:1:1;' for i in range(3))+b'U::;',
    'config-scalar-current-strict-option-explicit-invoke':
        b'S;'+WALK+b'T:1:99:14:precision:29;I;'+WALK+b'R:1:14:precision:29;U::;',
    'config-scalar-current-float-api-after-data-destructor':
        b'B;G;'+WALK+b'D:14;M:3;A:3:1.23:1:1:1;F:1;U::;',
}
