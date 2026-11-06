<?php
namespace ScopedIncludedMethodCache144;
enum Target { case A; }
function publish($install) {
    if ($install) { function is_callable($v,$s,$n) { echo 'USER:', $n, '|'; return false; } }
    return false;
}
function retire($value) {
    unset($GLOBALS['source']);
    echo $GLOBALS['weak']->get() === null ? 'gone-early|' : 'held|';
    return $value;
}
class Host {
    public static function query($install) {
        $name='OLD'; $ok=is_callable([Target::class,'cases'],publish($install),$name);
        echo 'query:', (int)$ok, ':', $name, '|';
    }
}
class Producer {
    public function install() {
        include 'cold.php';
        echo 'raw|'; Host::query(false);
        include 'warm.php';
    }
}
class ChildProducer extends Producer {}
$producer=new ChildProducer(); $producerWeak=\WeakReference::create($producer);
$producer->install(); unset($producer);
echo $producerWeak->get() === null ? 'producer-gone|' : 'producer-pinned|';
unset($producerWeak);
$cold=ColdCapture; $warm=WarmCapture;
echo 'cold|'; $cold(false);
$source=clone $cold; $weak=\WeakReference::create($source);
echo 'private-copy|'; $source(true);
echo 'cold-again|'; $cold(false);
echo 'warm|'; $warm(false);
$fresh=clone $cold; echo 'fresh|'; $fresh(false);
$shared=clone $warm; echo 'shared-copy|'; $shared(false);
echo 'retire|'; $source(retire(false));
echo $weak->get() === null ? 'source-gone|' : 'pinned|';
$fresh_weak=\WeakReference::create($fresh); $shared_weak=\WeakReference::create($shared);
unset($fresh,$shared);
echo $fresh_weak->get() === null ? 'fresh-gone|' : 'fresh-pinned|';
echo $shared_weak->get() === null ? 'shared-gone|' : 'shared-pinned|';
unset($weak,$fresh_weak,$shared_weak,$cold,$warm); echo 'done|';
