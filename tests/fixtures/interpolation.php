<?php
$a = "a $x b {$x} c ${x} d ${$name} e $a[0] f $a[key] g $o->p h {$o->p} i {$a['key']}";
$a = `echo $x {$a[0]}`;
$a = <<<END
    a $x {$o->p}
    END;
$b = <<<'END'
    $not\interpolated
    END;
$c = <<<"Q"
Q;
