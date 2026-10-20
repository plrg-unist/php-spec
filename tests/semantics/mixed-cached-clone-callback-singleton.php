<?php
#[AllowDynamicProperties]
class MixedCallback118 {
    public int $tag = 1;
    public function __clone(): void {
        echo 'C|';
        $this->tag = 2;
        $this->extra = 7;
        unset($this->obsolete);
        $this->tail = 8;
        foreach ($this as $key => $entry) { echo $key, ':', $entry, '|'; }
        unset($key, $entry);
        echo 'c|';
    }
}
echo 'U:';
$source = new MixedCallback118();
$source->extra = 1;
$source->obsolete = 3;
$alias =& $source->extra;
unset($alias);
foreach ($source as $key => $entry) {}
unset($key, $entry);
$copy = clone $source;
echo 'A|', $source->extra, '/', $copy->extra, '|';
$source->extra = 9;
echo 'B|', $source->extra, '/', $copy->extra, '|';
foreach ($source as $key => $entry) { echo $key, ':', $entry, '|'; }
unset($key, $entry, $source, $copy);
echo 'E|';
