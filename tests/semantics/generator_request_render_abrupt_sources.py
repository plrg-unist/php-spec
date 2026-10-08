#!/usr/bin/env python3
"""Focused C-root renderer-throw originals; native outcomes initially provisional."""
import generator_request_render_abrupt_peer_sources as peer

CASES = {
    'request-render-inner-release-before-bailout': (b'<?php\nclass PayloadRenderRelease{function __destruct(){echo "D";}}\nclass LaterRenderRelease{function __destruct(){echo "Q";}}\nclass InnerRenderRelease extends Exception{function __destruct(){global $wg,$wp;echo "I",(int)($wg->get()!==null),":",(int)($wp->get()!==null);error_reporting(0);}}\nclass RenderReleaseException extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);throw new InnerRenderRelease("render");}function __destruct(){global $wg,$wp;echo "O",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}}\nfunction requestRenderRelease(){try{yield new PayloadRenderRelease;}finally{echo "F";throw new RenderReleaseException("new");}}\n$later=new LaterRenderRelease;$g=requestRenderRelease();$wg=WeakReference::create($g);$keepGen=&$wg;\n$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";\n', b'C|FT1:1I1:1', 255),
    'request-handler-render-throws': (b'<?php\nclass PayloadHandlerRender{function __destruct(){echo "D";}}\nclass LaterHandlerRender{function __destruct(){echo "Q";}}\nclass HandlerRenderException extends Exception{function __toString():string{global $wg,$wp,$we;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($we->get()!==null);throw new Exception("render-handler");}}\nfunction handlerRenderAbort($e){global $we;echo "H";$we=WeakReference::create($e);throw new HandlerRenderException("handler");}\nset_exception_handler("handlerRenderAbort");\nfunction requestHandlerRender(){try{yield new PayloadHandlerRender;}finally{echo "F";throw new Exception("new");}}\n$later=new LaterHandlerRender;$g=requestHandlerRender();$wg=WeakReference::create($g);$keepGen=&$wg;\n$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";\n', b'C|FHT1:1:1', 255),
}

def main():
    driver = peer.driver
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'request-render-inner-release-before-bailout': b'Fatal error: Uncaught InnerRenderRelease: render',
        'request-handler-render-throws': b'Fatal error: Uncaught Exception: render-handler',
    }
    driver.WATCHED += peer.EXTRA_WATCHED + ["tests/semantics/generator_request_render_abrupt_sources.py"]
    return driver.main()

if __name__ == "__main__":
    raise SystemExit(main())
