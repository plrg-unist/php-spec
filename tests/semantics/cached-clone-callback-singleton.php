<?php
class CachedCallback113 {
    public int $value = 1;
    public int $tag = 1;
    public function __clone(): void {
        echo 'C|';
        $this->value = 7;
        $this->tag = 2;
        foreach ($this as $key => $entry) { echo $key, ':', $entry, '|'; }
        unset($key, $entry);
        echo 'c|';
    }
}
$source = new CachedCallback113();
$alias =& $source->value;
unset($alias);
foreach ($source as $key => $entry) {}
unset($key, $entry);
echo 'U:';
$copy = clone $source;
echo $source->value, '/', $copy->value, '|';
unset($source, $copy);
echo 'E|';
