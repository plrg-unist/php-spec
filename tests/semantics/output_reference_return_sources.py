#!/usr/bin/env python3
"""Raw reference output returns, late scalar conversion and callback demand."""
from pathlib import Path

import output_api_failure_sources as common


def scalar(value, byref=True, local=False):
    declaration = b'function ' + (b'&' if byref else b'') + b'h($b,$p){'
    declaration += (b'$r=' + value + b';') if local else b'global $r;'
    return (b'<?php echo "P";$r=' + value + b';' + declaration
            + b'return $r;}ob_start("h",1);$x=print "A";$s=ob_get_status();'
            b'ob_end_clean();echo "|".$x.":".$s["flags"];')


CASES = {
    'ref-false': (scalar(b'false'), b'P|1:20593'),
    'ref-true': (scalar(b'true'), b'P1|1:20593'),
    'ref-null': (scalar(b'null'), b'P|1:20593'),
    'ref-integer': (scalar(b'-42'), b'P-42|1:20593'),
    'ref-float': (scalar(b'1.234567'), b'P1.234567|1:20593'),
    'ref-string': (scalar(b'"X\\0Y"'), b'PX\0Y|1:20593'),
    'value-false': (scalar(b'false', byref=False), b'PA|1:12401'),
    'local-cell-true': (scalar(b'true', local=True), b'P1|1:20593'),
    'literal-notice': (
        b'<?php echo "P";$n=0;set_error_handler(function() {global $n;$n++;return true;});'
        b'function &h($b,$p){return true;}ob_start("h");echo "A";'
        b'$v=ob_get_flush();echo "|".$v.":".$n;', b'P1|A:1'),
    'notice-throw-defined': (
        b'<?php echo "P";$e=new Exception;$x=99;'
        b'set_error_handler(function(){global $e;throw $e;});'
        b'function &h($b,$p){return true;}ob_start("h");echo "A";'
        b'try{$x=ob_get_flush();}catch(Exception $c){'
        b'echo "|".($c===$e?"C":"N").":".$x.":".ob_get_level();}', b'P1|C:99:0'),
    'cleanup-throw-defined': (
        b'<?php echo "P";$e=new Exception;$r=false;$x=99;'
        b'class D{function __destruct(){global $r,$e;$r=true;throw $e;}}'
        b'function &h($b,$p){global $r;$d=new D;return $r;}ob_start("h");echo "A";'
        b'try{$x=ob_get_flush();}catch(Exception $c){echo "|".($c===$e?"C":"N").'
        b'":".$x.":".($r===true?"T":"N").":".ob_get_level();}', b'P1|C:99:T:0'),
    'warning-mutates-and-throws': (
        b'<?php echo "P";$e=new Exception;$r=false;$x=99;'
        b'set_error_handler(function(){global $r,$e;$r=true;throw $e;});'
        b'function &h($b,$p){global $r;echo "H";return $r;}ob_start("h");echo "A";'
        b'try{$x=ob_get_flush();}catch(Exception $c){echo "|".$x.":".'
        b'($r===true?"T":"N").":".ob_get_level();}', b'P1|99:T:0'),
    'warning-rebinds-alias': (
        b'<?php echo "P";$r=true;$q=false;set_error_handler(function(){'
        b'$GLOBALS["r"]=&$GLOBALS["q"];return true;});'
        b'function &h($b,$p){global $r;echo "H";return $r;}ob_start("h");echo "A";'
        b'$v=ob_get_flush();echo "|".$v.":".($r===false?"F":"N").":".'
        b'($q===false?"F":"N");', b'P1|A:F:F'),
    'unused-print-demand': (
        b'<?php echo "P";$r=true;$e=new Exception;$first=true;function &h($b,$p){'
        b'global $r,$e,$first;if($first){$first=false;return $r;}throw $e;}'
        b'ob_start("h",1);print "A";$s=ob_get_status();try{ob_end_clean();}'
        b'catch(Exception $c){}echo "|".$s["flags"].":".($r===true?"T":"N");', b'P1|20593:T'),
    'normal-final': (
        b'<?php echo "P";function &h($b,$p){$r=true;return $r;}'
        b'ob_start("h");echo "A";', b'P1'),
    'lower-api-warning-throw': (
        b'<?php echo "P";$e=new Exception;$r=true;$first=true;$x=99;'
        b'set_error_handler(function(){global $e;throw $e;});'
        b'function &h($b,$p){global $r,$first;if($first){$first=false;echo "H";}return $r;}'
        b'ob_start("h",1);ob_start();echo "A";try{$x=ob_flush();}catch(Exception $c){'
        b'$a=ob_get_status(true);$report=($c===$e?"C":"N").":".$x.":".$a[0]["flags"].'
        b'":".$a[1]["flags"].":".$a[1]["buffer_used"];}'
        b'ob_end_clean();ob_end_clean();echo "|".$report;', b'P1|C:99:20593:20592:0'),
}
CASES['discarded-for-demand'] = (
    CASES['unused-print-demand'][0].replace(b';print "A";', b';for(print "A";false;){};'),
    b'P1|20593:T')
CONTROLS = {
    'ref-array': scalar(b'[]'),
    'pending-final-ref': b'<?php echo "P";$e=new Exception;class D{function __destruct(){global $e;throw $e;}}function &h($b,$p){$r=true;$d=new D;return $r;}ob_start("h");echo "A";',
    'warning-changes-to-array': b'<?php echo "P";$r=false;set_error_handler(function(){global $r;$r=[];return true;});function &h($b,$p){global $r;echo "H";return $r;}ob_start("h");echo "A";ob_get_flush();echo "Z";',
}
CONTROL_REASONS = {
    'ref-array': 'non-scalar reference user output-handler return conversion',
    'pending-final-ref': 'pending FINAL reference output-handler return cleanup',
    'warning-changes-to-array': 'non-scalar reference user output-handler return conversion',
}

_common_fingerprint = common.fingerprint


def fingerprint():
    inputs = _common_fingerprint()
    inputs['tests/semantics/output_reference_return_sources.py'] = common.sha(Path(__file__))
    return inputs


def main():
    common.CASES = CASES
    common.CONTROLS = CONTROLS
    common.CONTROL_REASONS = CONTROL_REASONS
    common.fingerprint = fingerprint
    common.main()


if __name__ == '__main__':
    main()
