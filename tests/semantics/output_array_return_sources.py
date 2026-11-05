#!/usr/bin/env python3
"""Array output returns preserve captured owners through warnings and release."""
from pathlib import Path
import output_result_cleanup_sources as runner

ROOT = runner.ROOT
CASES = {'study-01-array-normal-getter': (b'<?php echo "P";$log="";set_error_handler(function($n,$m){glo'
                                  b'bal $log;$log=$n.":".$m;return true;});function h($b,$p){ret'
                                  b'urn [];}ob_start("h");echo "A";$v=ob_get_flush();echo "|".$v'
                                  b'.":".$log;',
                                  b'PArray|A:2:Array to string conversion'),
 'study-01-reference-warning-mutates-cell': (b'<?php echo "P";$r=[];set_error_handler(function(){gl'
                                             b'obal $r;$r=false;return true;});function &h($b,$p){g'
                                             b'lobal $r;return $r;}ob_start("h");echo "A";$v=ob_get'
                                             b'_flush();echo "|".$v.":".($r===false?"F":"N");',
                                             b'PArray|A:F'),
 'study-01-array-warning-throw-defined': (b'<?php echo "P";$e=new Exception;$x=99;set_error_hand'
                                          b'ler(function(){global $e;throw $e;});function h($b,$'
                                          b'p){return [];}ob_start("h");echo "A";try{$x=ob_get_f'
                                          b'lush();}catch(Exception $c){echo "|".($c===$e?"C":"N'
                                          b'").":".$x.":".ob_get_level();}',
                                          b'PArray|C:99:0'),
 'study-01-array-child-normal-cleanup': (b'<?php echo "P";$log="";set_error_handler(function(){glob'
                                         b'al $log;$log.="W";return true;});class D{function __dest'
                                         b'ruct(){global $log;$s=ob_get_status();$log.="D".$s["flag'
                                         b's"].":".$s["buffer_used"];echo "D";}}function h($b,$p){r'
                                         b'eturn [new D];}ob_start("h");echo "A";$v=ob_get_flush();'
                                         b'echo "|".$v.":".$log;',
                                         b'PArray|A:WD113:1'),
 'study-01-array-child-throw-replaces-warning': (b'<?php echo "P";$e=new Exception;$f=new Exception'
                                                 b';$x=99;set_error_handler(function(){global $e;th'
                                                 b'row $e;});class D{function __destruct(){global $'
                                                 b'f;echo "D";throw $f;}}function h($b,$p){return ['
                                                 b'new D];}ob_start("h");echo "A";try{$x=ob_get_flu'
                                                 b'sh();}catch(Exception $c){echo "|".($c===$f?"F":'
                                                 b'"N").":".($c->getPrevious()===$e?"E":"N").":".$x'
                                                 b'.":".ob_get_level();}',
                                                 b'PArray|F:E:99:0'),
 'study-01-array-callee-cleanup-throw': (b'<?php echo "P";$e=new Exception;$x=99;$warnings=0;set_er'
                                         b'ror_handler(function(){global $warnings;$warnings++;retu'
                                         b'rn true;});class D{function __destruct(){global $e;throw'
                                         b' $e;}}function h($b,$p){$d=new D;return [];}ob_start("h"'
                                         b');echo "A";try{$x=ob_get_flush();}catch(Exception $c){ec'
                                         b'ho "|".($c===$e?"C":"N").":".$x.":".$warnings.":".ob_get'
                                         b'_level();}',
                                         b'PArray|C:99:0:0'),
 'traces-01-api': (b'<?php\necho "P";$x=99;$log="";\nset_error_handler(function(){return true;}'
                   b');\nclass D{function __destruct(){global $log;$f=new Exception;$t=$f->getTrac'
                   b'e();$log=$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t['
                   b'0]["line"])?$t[0]["line"]:-1).":".(isset($t[1]["function"])?$t[1]["function"'
                   b']:"-").":".(isset($t[1]["file"])?"F":"-").":".(isset($t[1]["line"])?$t[1]["l'
                   b'ine"]:-1);throw $f;}}\nfunction h($b,$p){return [new D];}\nob_start("h");echo '
                   b'"A";\ntry{$x=ob_get_flush();}catch(Exception $c){}\necho "|".$x.":".$log;',
                   b'PArray|99:__destruct:I:-1:ob_get_flush:F:7'),
 'traces-01-vm': (b'<?php\necho "P";$x=99;$log="";\nset_error_handler(function(){return true;});\nc'
                  b'lass D{function __destruct(){global $log;$f=new Exception;$t=$f->getTrace();'
                  b'$log=$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[0]["'
                  b'line"])?$t[0]["line"]:-1).":".(isset($t[1]["function"])?$t[1]["function"]:"-'
                  b'").":".(isset($t[1]["file"])?"F":"-").":".(isset($t[1]["line"])?$t[1]["line"'
                  b']:-1);throw $f;}}\n$first=true;function h($b,$p){global $first;if($first){$fi'
                  b'rst=false;return [new D];}return false;}\nob_start("h",1);\ntry{$x=print "A";}'
                  b'catch(Exception $c){}\nob_end_clean();echo "|".$x.":".$log;',
                  b'PArray|99:__destruct:F:7:-:-:-1'),
 'phases-01-vm-child-output-late-produced': (b'<?php echo "P";$first=true;$log="";set_error_handler'
                                             b'(function($n){global $log;$log.="W".$n.";";return tr'
                                             b'ue;});class D{function __destruct(){global $log;$s=o'
                                             b'b_get_status();$log.="D".$s["flags"].":".$s["buffer_'
                                             b'used"].";";echo "D";}}function h($b,$p){global $firs'
                                             b't;if($first){$first=false;return [new D];}return tru'
                                             b'e;}ob_start("h",1);$x=print "A";$s=ob_get_status();o'
                                             b'b_end_clean();echo "|".$x.":".$s["flags"].":".$log;',
                                             b'PArray|1:53361:W2;D113:1;W8192;'),
 'phases-01-deprecation-before-array-warning-routing': (b'<?php echo "P";$log="";set_error_handler'
                                                        b'(function($n){global $log;$s=ob_get_stat'
                                                        b'us();$log.=$n.":".$s["flags"].";";if($n='
                                                        b'==8192){echo "B";}else{echo "W";}return '
                                                        b'true;});function h($b,$p){echo "H";retur'
                                                        b'n [];}ob_start("h");echo "A";$v=ob_get_f'
                                                        b'lush();echo "|".$v.":".$log;',
                                                        b'PBArray|A:8192:8305;2:113;'),
 'unique-ref-gc-transfer': (b'<?php echo "P";class D{function __destruct(){}}function eh($n,$m,$f,'
                            b'$l){if($n===8192){gc_collect_cycles();}return true;}set_error_handle'
                            b'r("eh");function &h($b,$p){$r=[new D];echo "H";return $r;}ob_start("'
                            b'h");echo "A";$x=ob_get_flush();echo "|".$x;',
                            b'PArray|A'),
 'shared-ref-gc-transfer': (b'<?php echo "P";$r=[];$r[]=1;class D{function __destruct(){}}function'
                            b' eh($n,$m,$f,$l){if($n===8192){gc_collect_cycles();}return true;}set'
                            b'_error_handler("eh");function &h($b,$p){global $r;echo "H";return $r'
                            b';}ob_start("h");echo "A";$x=ob_get_flush();echo "|".$x.":".$r[0];',
                            b'PArray|A:1'),
 'default-array-warning': (b'<?php echo "P";function h($b,$p){return [];}ob_start("h");echo "A";$'
                           b'v=ob_get_flush();echo "|".$v;',
                           b'PArray|A'),
 'promoted-ref-array': (b'<?php echo "P";$r=[];function &h($b,$p){global $r;return $r;}ob_start("h'
                        b'",1);$x=print "A";$s=ob_get_status();ob_end_clean();echo "|".$x.":".$s["'
                        b'flags"];',
                        b'PArray|1:20593'),
 'warning-changes-to-array': (b'<?php echo "P";$r=false;set_error_handler(function(){global $r;$'
                              b'r=[];return true;});function &h($b,$p){global $r;echo "H";return'
                              b' $r;}ob_start("h");echo "A";ob_get_flush();echo "Z";',
                              b'PArrayZ'),
 'get-clean-child-replacement': (b'<?php echo "P";$e=new Exception;$f=new Exception;$x=99;set_error'
                                 b'_handler(function(){global $e;throw $e;});class D{function __des'
                                 b'truct(){global $f;echo "D";throw $f;}}function h($b,$p){return ['
                                 b'new D];}ob_start("h");echo "A";try{$x=ob_get_clean();}catch(Exce'
                                 b'ption $c){echo "|".($c===$f?"F":"N").":".($c->getPrevious()===$e'
                                 b'?"E":"N").":".$x.":".ob_get_level();}',
                                 b'P|F:E:99:0'),
 'lower-api-warning-throw': (b'<?php echo "P";$e=new Exception;$first=true;$x=99;set_error_handler('
                             b'function(){global $first,$e;if($first){$first=false;throw $e;}return'
                             b' true;});function h($b,$p){return [];}ob_start("h",1);ob_start();ech'
                             b'o "A";try{$x=ob_flush();}catch(Exception $c){$a=ob_get_status(true);'
                             b'$r=($c===$e?"C":"N").":".$x.":".$a[0]["flags"].":".$a[1]["flags"].":'
                             b'".$a[1]["buffer_used"];}ob_end_clean();ob_end_clean();echo "|".$r;',
                             b'PArray|C:99:20593:20592:0'),
 'notice-array-defined': (b'<?php echo "P";$x=99;$level=0;class D{function __destruct(){throw ne'
                          b'w Exception("F");}}set_error_handler(function($n){global $level;$lev'
                          b'el=$n;throw new Exception("E");});function &h($b,$p){return [new D];'
                          b'}ob_start("h");echo "A";try{$x=ob_get_flush();}catch(Exception $c){e'
                          b'cho "|".$x.":".$level.":".$c->getMessage().":".$c->getPrevious()->ge'
                          b'tMessage().":".ob_get_level();}',
                          b'PArray|99:8:F:E:0'),
 'promoted-nonscalar-cleanup': (b'<?php echo "P";$e=new Exception;set_error_handler(function(){ret'
                                b'urn true;});class D{function __destruct(){global $e;throw $e;}}f'
                                b'unction h(&$b,$p){$b=new D;return [];}ob_start("h");echo "A";try'
                                b'{ob_end_clean();}catch(Exception $c){}',
                                b'P'),
 'promoted-nonscalar-handler': (b'<?php echo "P"; function h($b,$p){return [];} ob_start("h"); ech'
                                b'o "A"; ob_end_flush(); echo "Z";',
                                b'PArrayZ')}
STDERR = {'default-array-warning': b'Warning: Array to string conversion in {FILE} on line 1\n',
 'promoted-ref-array': b'Warning: Array to string conversion in {FILE} on line 1\nWarning: Array t'
                       b'o string conversion in {FILE} on line 1\n',
 'promoted-nonscalar-handler': b'Warning: Array to string conversion in {FILE} on line 1\n'}
CONTROLS = {
    'final-array': b'<?php echo "P";function h($b,$p){return [];}ob_start("h");echo "A";',
    'object-result': b'<?php echo "P";function h($b,$p){return new stdClass;}ob_start("h");echo "A";ob_get_flush();',
}
CONTROL_REASONS = {
    'final-array': 'FINAL array output-handler return conversion',
    'object-result': 'non-scalar user output-handler return conversion',
}
_original_fingerprint = runner.fingerprint

def fingerprint():
    inputs = _original_fingerprint()
    inputs['tests/semantics/output_array_return_sources.py'] = runner.common.sha(Path(__file__))
    return inputs

if __name__ == '__main__':
    runner.CASES = CASES
    runner.STDERR = STDERR
    runner.CONTROLS = CONTROLS
    runner.CONTROL_REASONS = CONTROL_REASONS
    runner.fingerprint = fingerprint
    runner.main()
