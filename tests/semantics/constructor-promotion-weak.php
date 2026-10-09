<?php
class RawArrayLastPayload19 {
    public function __construct(private WeakReference $target) {}
    public function __destruct() { echo 'D', (int)($this->target->get() === null), '|'; }
}
$target = new Fiber(static function () {
    try {
        echo 'B|';
        Fiber::suspend('Y');
        Fiber::suspend('Z');
    } finally { echo 'F|'; }
});
$weak = WeakReference::create($target);
echo $target->start(), '|';
$runner = new Fiber([$target, 'ReSuMe']);
unset($target);
echo $runner->start(new RawArrayLastPayload19($weak)), '|';
echo $runner->getReturn(), '|', (int)($weak->get() === null), '|', (int)$runner->isTerminated();
