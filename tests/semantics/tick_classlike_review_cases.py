"""Independent Interface/Trait/Enum emitter and uncalled-method Tick distinctions."""

CASES = {
    'review-early-interface-keeps-adjacent-declare-tick-suppressed': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1);
interface TickInterface39 { public function unused(); }
declare(ticks=2);
echo 'Z';
''', b'TZ'),
    'review-trait-uncalled-method-declarables-affect-following-markers': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1);
trait TickTrait39 {
    public function unused() { declare(ticks=2); echo 'BAD'; }
}
echo 'Z';
echo 'W';
''', b'TZWT'),
    'review-empty-enum-emitter-breaks-adjacency-without-outer-tick': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1);
declare(ticks=2);
echo 'P';
enum TickEmptyEnum39 {
    public function unused() { declare(ticks=2); echo 'BAD'; }
}
declare(ticks=3);
echo 'Z';
''', b'TPZT'),
}
