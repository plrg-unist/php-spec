<?php
class GC60Value { public $child = null; }
class GC60Child {
    public function __destruct() {
        global $map60, $loopKey60, $result60, $throw60,
               $mapWatch60, $keyWatch60, $oldWatch60, $expected60;
        $seen60 = $map60[$loopKey60];
        echo 'C|', (int) ($mapWatch60->get() === $map60), '|',
             (int) ($keyWatch60->get() === $loopKey60), '|',
             (int) ($oldWatch60->get() === null), '|',
             (int) ($seen60 === $expected60), '|',
             (int) ($result60 === 77), '|';
        if ($throw60) { throw new Exception('fresh-60'); }
    }
}
$throw60 = false;
$map60 = new WeakMap;
$key60 = new stdClass;
$scalarKey60 = new stdClass;
$old60 = new GC60Value;
$child60 = new GC60Child;
$old60->child = $child60;
$incoming60 = 23;
$expected60 = 23;
$map60[$key60] = $old60;
$map60[$scalarKey60] = 17;
$mapWatch60 = WeakReference::create($map60);
$keyWatch60 = WeakReference::create($key60);
$oldWatch60 = WeakReference::create($old60);
$childWatch60 = WeakReference::create($child60);
unset($old60, $child60);
$result60 = 77;
$continued60 = 0;
echo 'B|';
try {
    foreach ($map60 as $loopKey60 => $loopValue60) {
        $loopValue60 = 0;
        $result60 = $map60[$loopKey60] = $incoming60;
        $continued60 = 1;
        echo 'A|', (int) ($result60 === $incoming60), '|';
        break;
    }
} catch (Exception $error60) {
    $trace60 = $error60->getTrace();
    echo 'T|', $error60->getMessage(), '|', $trace60[0]['function'], '|',
         (int) ($result60 === 77), '|', $continued60, '|';
}
echo 'R|', (int) ($result60 === 77), '|',
     (int) ($result60 === $incoming60), '|', $continued60, '|',
     (int) ($loopValue60 === 0), '|',
     (int) ($map60[$key60] === $incoming60), '|',
     (int) ($oldWatch60->get() === null), '|',
     (int) ($childWatch60->get() === null), '|';
unset($map60);
echo 'M|', (int) ($mapWatch60->get() === null), '|',
     (int) ($incoming60 === $expected60), '|';
unset($result60);
echo 'V|', (int) ($incoming60 === $expected60), '|';
unset($incoming60, $expected60);
unset($key60, $scalarKey60, $loopKey60);
echo 'K|', (int) ($keyWatch60->get() === null), '|';
