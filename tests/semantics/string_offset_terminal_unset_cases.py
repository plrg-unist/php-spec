"""Terminal UNSET_DIM rejects authenticated string carriers without key casts."""

CASES = {
    'terminal-unset-authenticated-carriers': b"<?php\n$a='ab';$left='a';$right='b';$b=$left.$right;\ntry { unset($a[INF]); } catch (Error $e) { echo $e->getMessage(),'|',$e->getLine(),'|',$a,';'; }\ntry { unset($b['bad']); } catch (Error $e) { echo $e->getMessage(),'|',$e->getLine(),'|',$b; }\n",
}
