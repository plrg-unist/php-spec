"""Ordinary nested string unset errors and delayed dimension operands."""

CASES = {
    'nested-unset-leading-numeric-final-assignment': b"<?php\n$s='ab';$last=0;\ntry { unset($s['0x'][$last=7]); } catch (Error $e) { echo $e->getMessage(),'|',$e->getLine(),'|',$last,'|',$s; }\n",
    'nested-unset-late-missing-final-cv': b"<?php\n$s='ab';\ntry { unset($s[0][$missing]); } catch (Error $e) { echo $e->getMessage(),'|',$s,'|',(int)isset($missing); }\n",
    'nested-unset-invalid-key-final-assignment': b"<?php\n$s='ab';$last=0;\ntry { unset($s[[]][$last=9]); } catch (Error $e) { echo $e->getMessage(),'|',$last,'|',$s; }\n",
    'nested-unset-live-inner-cv': b"<?php\n$s='ab';$k='0x';\ntry { unset($s[$k][$k='bad']); } catch (Error $e) { echo $e->getMessage(),'|',$k,'|',$s; }\n",
}
