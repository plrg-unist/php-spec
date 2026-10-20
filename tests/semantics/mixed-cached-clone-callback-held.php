<?php
#[AllowDynamicProperties]
class MixedCallback118 {
    public int $tag = 1;
    public function __clone(): void {
        echo 'C|';
        $this->tag = 2;
        $this->extra = 7;
        foreach ($this as $key => $entry) { echo $key, ':', $entry, '|'; }
        unset($key, $entry);
        echo 'c|';
    }
}
echo 'H:';
$source = new MixedCallback118();
$source->extra = 1;
$alias =& $source->extra;
foreach ($source as $key => $entry) {}
unset($key, $entry);
$copy = clone $source;
echo 'A|', $source->extra, '/', $copy->extra, '/', $alias, '|';
unset($source->extra);
$alias = 9;
echo 'B|', $copy->extra, '/', $alias, '|';
unset($source);
unset($copy->extra);
$alias = 'free';
echo $alias, '|';
unset($copy, $alias);
echo 'E|';
