"""By-value Iterator caches stay separate from declared field replacements."""

from array_iterator_fields_cases import CASES as REFERENCE_FIELDS


POOLED = REFERENCE_FIELDS['array-iterator-fields-byval-boundary']
LAST_DATA = REFERENCE_FIELDS['array-iterator-fields-last-data'].replace(
    b'function &current()', b'function current()', 1)
KEY_THROW = REFERENCE_FIELDS['array-iterator-fields-key-throw'].replace(
    b'function &current()', b'function current()', 1)
AGGREGATE = POOLED.replace(
    b'<?php\n', b'''<?php
class ByvalFieldBag implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["it"];}
}
''', 1).replace(
    b'$dest=[4=>8,...$it,$tail++];',
    b'$bag=new ByvalFieldBag;$dest=[4=>8,...$bag,$tail++];', 1).replace(
    b'unset($dest,$escaped,$saved,$pool,$leaf,$other,$marker,$watch,$tail);',
    b'unset($bag,$dest,$escaped,$saved,$pool,$leaf,$other,$marker,$watch,$tail);', 1)

CASES = {
    'array-iterator-byval-fields-pooled': POOLED,
    'array-iterator-byval-fields-last-data': LAST_DATA,
    'array-iterator-byval-fields-key-throw': KEY_THROW,
    'array-iterator-byval-fields-aggregate': AGGREGATE,
    'array-iterator-byval-fields-no-destructor': b'''<?php
class ByvalFieldsNoDestructor implements Iterator {
    public $first;public $second;public $row;public $mark;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        $this->first[0][0]=33;$this->second[0][0]=44;$this->row[0][0]=55;
        $GLOBALS["leaf"]=8;$this->mark++;
        echo "K:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$this->mark,";";
        return "row";
    }
    public function next():void {$this->position++;echo "N;";}
}
$seed=3;$child=[$seed];$leaf=2;$marker=0;
$it=new ByvalFieldsNoDestructor;$it->first=[$child,&$leaf];
$it->second=$it->first;$it->row=$it->first;$it->mark=&$marker;
$saved=$it->first;$watch=WeakReference::create($it);unset($child);
echo "P:",$watch->get()===$it,";";
$dest=[...$it];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$saved[0][0],":",$saved[1],":",$marker,":",$watch->get()===null,":",isset($it),";";
unset($leaf);$dest["row"][1]=66;$dest["row"][0][0]=77;
echo "S:",$dest["row"][0][0],":",$dest["row"][1],":",$saved[0][0],":",$saved[1],";";
unset($dest,$saved,$seed,$marker,$watch);
echo "U:",isset($it),":",isset($dest),":",isset($saved),";";
''',
    'array-iterator-byval-fields-typed-boundary': POOLED.replace(
        b'public $row;', b'public array $row;', 1),
}

BOUNDARIES = {
    'array-iterator-byval-fields-typed-boundary':
        'array Iterator unpack outside initialized Iterator domain',
}
