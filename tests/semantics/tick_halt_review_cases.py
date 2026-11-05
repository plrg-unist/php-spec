"""A split Halt statement ticks with its compiled offset already available."""

SOURCE = b'''<?php
function t(){
    $e=new Exception;
    echo 'T';
    echo $e->getTrace()[0]['line'];
    echo ':';
    echo constant('__COMPILER_HALT_OFFSET__');
    throw new Exception('stop');
}
function h($e){echo 'C';}
function s(){echo 'Z';}
register_tick_function('t');
set_exception_handler('h');
register_shutdown_function('s');
class Enable48 {public function unused(){declare(ticks=1);}}
__halt_compiler
(
)
;
<?php echo 'BAD-PAYLOAD'; ?>
'''

OFFSET = SOURCE.index(b';', SOURCE.rindex(b'__halt_compiler')) + 1
CASES = {
    'review-split-halt-tick-reads-offset-and-aborts-with-inert-payload':
        (SOURCE, b'T19:' + str(OFFSET).encode() + b'CZ'),
}
