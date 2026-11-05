"""A real unbracketed namespace header Tick precedes its normalized body."""

CASES = {
    'review-unbracketed-header-line-and-abort-before-pending-body-class': (b'''<?php
namespace First46;
$n=0;
function t(){
    global $n; $n=$n+1; echo 'T';
    if($n===1){
        $at=new \\Exception;
        echo '['.$at->getTrace()[0]['line'].']';
        try{\\Second46\\Pending46::VALUE;echo 'BAD';}
        catch(\\Error $absent){echo 'N';}
        throw new \\Exception('stop');
    }
}
function h($e){
    echo 'C';
    try{\\Second46\\Pending46::VALUE;echo 'BAD';}
    catch(\\Error $absent){echo 'N';}
}
\\register_tick_function('First46\\t');
\\set_exception_handler('First46\\h');
interface Ready46 {}
class Barrier46 implements Ready46 { public function unused(){declare(ticks=1);} }
namespace
Second46;
class Pending46 implements \\First46\\Ready46 { public const VALUE=7; }
echo 'BAD';
''', b'T[24]NCN'),
}
