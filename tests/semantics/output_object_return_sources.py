#!/usr/bin/env python3
"""Object output returns; slow Notice originals use the reached front."""
import sys
from pathlib import Path
import output_result_cleanup_sources as runner

ROOT = runner.ROOT
CASES = {'normal-vm-late-produced': (b'<?php echo "P";$log="";$n=0;set_error_handler(function($l){$GLOBALS[\'log\'].='
                             b'"E$l;";return true;});class T{function __toString(){global $log;$log.="S".ob'
                             b'_get_status()[\'flags\'].":".ob_get_contents().";";echo "S";return "H";}functi'
                             b'on __destruct(){global $log;$log.="D".ob_get_contents().";";echo "D";}}funct'
                             b"ion h($b,$p){global $n;return $n++===0?new T:null;}ob_start('h',1);$x=print "
                             b'"A";$f=ob_get_status()[\'flags\'];ob_end_clean();echo "|$x:$f:$log";',
                             b'PH|1:53361:S113:A;DAS;E8192;'),
 'normal-api-getter': (b'<?php echo "P";$log="";class T{function __toString(){global $log;$log.="S".ob_get_st'
                       b'atus()[\'flags\'].":".ob_get_contents().";";echo "S";return "H";}function __destru'
                       b'ct(){global $log;$log.="D".ob_get_contents().";";echo "D";}}function h($b,$p){return'
                       b' new T;}ob_start(\'h\');echo \'A\';$x=ob_get_flush();echo "|$x:$log";',
                       b'PH|A:S113:A;DAS;'),
 'cast-throw-vm': (b'<?php echo "P";$n=0;$x=99;class T{function __toString(){throw new Exception(\'E\');}fu'
                   b'nction __destruct(){echo "D";}}function h($b,$p){global $n;return $n++===0?new T:null;}s'
                   b"et_error_handler(function(){return true;});ob_start('h',1);try{$x=print 'A';}catch(Throw"
                   b'able $e){$m=$e->getMessage();$f=ob_get_status()[\'flags\'];}ob_end_clean();echo "|$x:$'
                   b'm:$f:".ob_get_level();',
                   b'P|99:E:53361:0'),
 'cast-success-dtor-throw-api': (b'<?php echo "P";$x=99;class T{function __toString(){return \'H\';}function '
                                 b"__destruct(){echo 'D';throw new Exception('F');}}function h($b,$p){retur"
                                 b"n new T;}ob_start('h');echo 'A';try{$x=ob_get_flush();}catch(Throwable $"
                                 b'e){$m=$e->getMessage();}echo "|$x:$m:".ob_get_level();',
                                 b'PH|99:F:0'),
 'cast-failure-standard-object': (b'<?php echo "P";$n=0;$x=99;class T{function __destruct(){echo \'D\';}}f'
                                  b'unction h($b,$p){global $n;return $n++===0?new T:null;}set_error_handler'
                                  b"(function(){return true;});ob_start('h',1);try{$x=print 'A';}catch(Throw"
                                  b"able $e){$m=$e->getMessage();$c=get_class($e);$f=ob_get_status()['flags'"
                                  b'];}ob_end_clean();echo "|$x:$c:$m:$f";',
                                  b'P|99:Error:Object of class T could not be converted to string:53361'),
 'cast-failure-dtor-replaces-error': (b'<?php echo "P";$x=99;class T{function __destruct(){throw new Excepti'
                                      b"on('F');}}function h($b,$p){return new T;}ob_start('h');echo 'A';try"
                                      b'{$x=ob_get_flush();}catch(Throwable $e){echo "|$x:".$e->getMessage()'
                                      b".':'.get_class($e->getPrevious()).':'.$e->getPrevious()->getMessage("
                                      b").':'.ob_get_level();}",
                                      b'P|99:F:Error:Object of class T could not be converted to string:0'),
 'pending-deprecation-skips-cast': (b'<?php echo "P";$x=99;$log="";class T{function __toString(){global $l'
                                    b"og;$log.='S';return 'H';}function __destruct(){global $log;$log.='D'"
                                    b";}}function h($b,$p){echo 'Q';return new T;}set_error_handler(functi"
                                    b"on(){throw new Exception('E');});ob_start('h');echo 'A';try{$x=ob_ge"
                                    b't_flush();}catch(Throwable $e){$m=$e->getMessage();}restore_error_ha'
                                    b'ndler();echo "|$x:$m:$log:".ob_get_level();',
                                    b'P|99:E:D:0'),
 'cast-defined-string-quiet-callee-cleanup-throw': (
     b"<?php echo 'P';$x=99;class D{function __destruct(){throw new Exception('E');}}"
     b"class T{function __toString(){$d=new D;return 'H';}}function h($b,$p){return new T;}"
     b"ob_start('h');echo 'A';try{$x=ob_get_flush();}catch(Throwable $e){$m=$e->getMessage();}"
     b'echo "|$x:$m:".ob_get_level();', b'PH|99:E:0'),
 'cast-fresh-api-trace': (b"<?php\n echo 'P';$x=99;\n class T{function __toString(){throw new Exception('E"
                          b"');}}\n function h($b,$p){return new T;}\n ob_start('h');\n echo 'A';\n try{$x=o"
                          b'b_get_flush();}catch(Throwable $e){$t=$e->getTrace();$a=$t[0];$b=$t[1];echo "|$x'
                          b':".$a[\'function\'].\':\'.(isset($a[\'file\'])?\'F\':\'I\').\':\'.$b[\'functi'
                          b"on'].':'.(isset($b['file'])?'F':'I').':'.$b['line'];}\n",
                          b'P|99:__toString:I:ob_get_flush:F:7'),
 'cast-fresh-vm-trace': (b"<?php\n echo 'P';$x=99;$n=0;\n class T{function __toString(){throw new Exception('"
                         b"E');}}\n function h($b,$p){global $n;return $n++===0?new T:null;}\n ob_start('h',1"
                         b");\n $m='';\n try{$x=print 'A';}catch(Throwable $e){$a=$e->getTrace()[0];$m=$a['fu"
                         b"nction'].':'.(isset($a['file'])?'F':'I').':'.(isset($a['line'])?$a['line']:-1);}"
                         b'\n ob_end_clean();echo "|$x:$m";\n',
                         b'P|99:__toString:F:7'),
 'cast-weak-return-coercion': (b"<?php echo 'P';class T{function __toString(){return 42;}}function h($b,$p){r"
                               b'eturn new T;}ob_start(\'h\');echo \'A\';$x=ob_get_flush();echo "|$x";',
                               b'P42|A'),
 'cast-strict-return-type-error': (b"<?php declare(strict_types=1);echo 'P';$x=99;class T{function __toString"
                                   b"(){return 42;}}function h($b,$p){return new T;}ob_start('h');echo 'A';tr"
                                   b'y{$x=ob_get_flush();}catch(Throwable $e){echo "|$x:".get_class($e).\''
                                   b":'.$e->getMessage().':'.ob_get_level();}",
                                   b'P|99:TypeError:T::__toString(): Return value must be of type string, int'
                                   b' returned:0'),
 'unique-method-reference-string': (b"<?php echo 'P';class T{function &__toString(){$s='H';return $s;}func"
                                    b"tion __destruct(){}}function h($b,$p){return new T;}ob_start('h');ec"
                                    b'ho \'A\';$x=ob_get_flush();echo "|$x";',
                                    b'PH|A'),
 'nested-existing-stringable-cast': (b"<?php echo 'P';class U{function __toString(){return 'H';}}class T{fu"
                                     b'nction __toString(){return (string)new U;}}function h($b,$p){return '
                                     b'new T;}ob_start(\'h\');echo \'A\';$x=ob_get_flush();echo "|$x";',
                                     b'PH|A'),
 'reference-alias-release-during-cast-strict-check': (b'<?php echo "P";$log="";$r=null;class T{function __to'
                                                      b"String(){global $r,$log;$r=false;$log.='S';return 'H"
                                                      b"';}function __destruct(){global $log;$log.='D';}}$r="
                                                      b'new T;function &h($b,$p){global $r;return $r;}ob_sta'
                                                      b'rt(\'h\');echo \'A\';$x=ob_get_flush();echo "|$x:$lo'
                                                      b'g:".($r===false?\'F\':\'O\');',
                                                      b'PH|A:SD:F'),
 'cast-reference-string-strict-check': (b"<?php echo 'P';$r='H';class T{function &__toString(){global $r;r"
                                        b"eturn $r;}}function h($b,$p){return new T;}ob_start('h');echo 'A"
                                        b'\';$x=ob_get_flush();echo "|$x:$r:".($r===\'H\'?\'S\':\'X\');',
                                        b'PH|A:H:S'),
 'fresh-unique-ref-object-precast-gc': (b"<?php echo 'P';$log='';function eh($n,$m,$f,$l){if($n===8192){gc"
                                        b"_collect_cycles();}return true;}set_error_handler('eh');class T{"
                                        b"function __toString(){global $log;$log.='S';return 'H';}function"
                                        b" __destruct(){global $log;$s=ob_get_status();$log.='D'.$s['flags"
                                        b"'];}}function &h($b,$p){$r=new T;echo 'Q';return $r;}ob_start('h"
                                        b'\');echo \'A\';$x=ob_get_flush();echo "|$x:$log";',
                                        b'PH|A:SD113'),
 'method-reference-notice-framed': (b"<?php echo 'P';$x=99;class T{function &__toString(){return 'H';}func"
                                    b'tion __destruct(){}}function h($b,$p){return new T;}set_error_handle'
                                    b"r(function(){throw new Exception('N');});ob_start('h');echo 'A';try{"
                                    b'$x=ob_get_flush();}catch(Throwable $e){$m=$e->getMessage();}echo "|$'
                                    b'x:$m:".ob_get_level();',
                                    b'PH|99:N:0'),
 'method-reference-notice-unframed': (b"<?php echo 'P';$x=99;class T{function &__toString(){return 'H';}}fun"
                                      b'ction h($b,$p){return new T;}set_error_handler(function(){throw new '
                                      b"Exception('N');});ob_start('h');echo 'A';try{$x=ob_get_flush();}catc"
                                      b'h(Throwable $e){$m=$e->getMessage();}echo "|$x:$m:".ob_get_level();',
                                      b'PH|99:N:0'),
 'stdclass-cast-error': (b"<?php echo 'P';$x=99;function h($b,$p){return new stdClass;}ob_start('h');echo '"
                         b'A\';try{$x=ob_get_flush();}catch(Throwable $e){echo "|$x:".get_class($e).\':\'.'
                         b"$e->getMessage().':'.ob_get_level();}",
                         b'P|99:Error:Object of class stdClass could not be converted to string:0')}
STDERR = {}
CONTROLS = {'internal-object': b"<?php echo 'P';function h($b,$p){return new Exception('E');}ob_start('h');echo 'A';o"
                    b'b_get_flush();'}
CONTROL_REASONS = {'internal-object': 'non-scalar user output-handler return conversion'}
REACHED_ONLY_CASES = {'method-reference-notice-framed', 'method-reference-notice-unframed'}
_original_fingerprint = runner.fingerprint

def fingerprint():
    inputs = _original_fingerprint()
    inputs['tests/semantics/output_object_return_sources.py'] = runner.common.sha(Path(__file__))
    return inputs

if __name__ == '__main__':
    # These exact originals exceed public60 and retain zero source credit.
    # The separate state suite checks their genuine owners and full resumption.
    if '--select' not in sys.argv:
        sys.argv.extend(['--select', ','.join([name for name in CASES if name not in REACHED_ONLY_CASES] + list(CONTROLS))])
    runner.CASES = CASES
    runner.STDERR = STDERR
    runner.CONTROLS = CONTROLS
    runner.CONTROL_REASONS = CONTROL_REASONS
    runner.fingerprint = fingerprint
    runner.main()
