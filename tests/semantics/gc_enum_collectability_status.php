<?php
enum GcEnumCollect08 { case A; }
gc_disable();
echo 'Z|', gc_collect_cycles(), '|', gc_status()['roots'], '|';
$case = GcEnumCollect08::A;
$weak = WeakReference::create($case);
unset($case);
echo gc_status()['roots'], '|', ($weak->get() === GcEnumCollect08::A ? 'alive' : 'BAD'), '|';
$cycle = new stdClass;
$cycle->self = $cycle;
unset($cycle);
echo gc_status()['roots'], '|', gc_collect_cycles(), '|', gc_status()['roots'], '|';
echo ($weak->get() === GcEnumCollect08::A ? 'same' : 'BAD'), '|END';
