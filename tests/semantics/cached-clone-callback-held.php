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
foreach ($source as $key => $entry) {}
unset($key, $entry);
echo 'H:';
$copy = clone $source;
echo $alias, '/', $source->value, '/', $copy->value, '|';
unset($source->value);
try { $alias = 'bad'; } catch (TypeError $caught) { echo 'T|'; }
echo $alias, '|';
unset($copy->value);
$alias = 'free';
echo $alias, '|';
unset($source, $copy, $alias, $caught);
echo 'E|';
