"""A literal eval import uses the request counter before pending class work."""

CASES = {
    'review-eval-namespace-import-shares-counter-and-aborts-pending-class': (b'''<?php
$n=0;
function t(){
    global $n; $n=$n+1; echo 'T';
    echo \\Dyn47\\Trigger47::VALUE;
    try{\\Dyn47\\Pending47::VALUE;echo 'BAD';}
    catch(Error $absent){echo 'N';}
    throw new Exception('stop');
}
register_tick_function('t');
declare(ticks=2);
declare(ticks=0);
try{
    eval('namespace Dyn47;
interface Ready47 {}
class Trigger47 { public const VALUE=7; public function unused(){declare(ticks=2);} }
use Exception as Imported47;
class Pending47 implements Ready47 { public const VALUE=9; }
echo "BAD";');
    echo 'BADMAIN';
}
catch(Exception $e){echo 'C';}
try{\\Dyn47\\Pending47::VALUE;echo 'BAD';}
catch(Error $absent){echo 'N';}
echo $n;
echo 'Z';
''', b'T7NCN1Z'),
}
