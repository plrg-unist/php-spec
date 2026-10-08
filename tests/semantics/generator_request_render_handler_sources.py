#!/usr/bin/env python3
"""Request renderer handler/warning ordering with observed native controls."""
import generator_request_render_handler_peer_sources as peer

driver = peer.driver

UNSUPPORTED = {
    'request-render-warning-reads-live-cache': (
        b'''<?php
class PayloadRenderWarning{function __destruct(){echo "D";}}
class LaterRenderWarning{function __destruct(){echo "Q";}}
function handledWarningInner($e){global $wi;echo "H";$wi=WeakReference::create($e);}
function handledRenderWarning($level,$message,$file,$line){global $wi,$wo,$wg,$wp;echo "W",(int)($wi->get()===null),":",(int)(get_exception_handler()==="handledWarningInner"),":",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($file==="Unknown"),":",(int)($line===0);$wo->get()->remember();return true;}
class RenderWarningException extends Exception{function remember(){$this->message="changed";parent::__toString();}function __toString():string{global $wo,$wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);$wo=WeakReference::create($this);set_exception_handler("handledWarningInner");set_error_handler("handledRenderWarning");throw new Exception("render");}function __destruct(){global $wg,$wp;echo "O",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}}
function requestRenderWarning(){try{yield new PayloadRenderWarning;}finally{echo "F";throw new RenderWarningException("new");}}
$later=new LaterRenderWarning;$g=requestRenderWarning();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1HW1:1:1:1:1:1O1:1', 'Generator request fatal rendering exception', 255),
}
CASES = {name: (row[0], row[1], row[3]) for name, row in UNSUPPORTED.items()}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'request-render-warning-reads-live-cache': b'Fatal error: Uncaught RenderWarningException: changed',
    }
    driver.WATCHED += peer.EXTRA_WATCHED + [
        'tests/semantics/generator_request_render_handler_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
