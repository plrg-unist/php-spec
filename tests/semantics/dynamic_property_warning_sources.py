#!/usr/bin/env python3
"""Ordinary dynamic-property warning continuation and operand lifetime controls."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'dynamic-reentry-table': b"<?php\nclass DynamicReentryTable18 {}\n$object = new DynamicReentryTable18();\nset_error_handler(function ($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\nforeach ($object as $key => $value) {\n    echo $key, '=', $value, '|';\n}\necho $object->x, '|done';\n",
    'dynamic-borrowed-rhs': b"<?php\nclass DynamicBorrowedRhs18 {}\n$object = new DynamicBorrowedRhs18();\n$rhs = 7;\nset_error_handler(function ($level, $message, $file, $line) {\n    echo 'warning|';\n    $GLOBALS['rhs'] = 9;\n    return true;\n});\necho ($object->x = $rhs), '|', $object->x, '|', $rhs, '|done';\n",
    'dynamic-computed-rhs': b"<?php\nclass DynamicComputedRhs18 {}\n$object = new DynamicComputedRhs18();\n$rhs = 7;\nset_error_handler(function ($level, $message, $file, $line) {\n    echo 'warning|';\n    $GLOBALS['rhs'] = 9;\n    return true;\n});\necho ($object->x = $rhs + 0), '|', $object->x, '|', $rhs, '|done';\n",
    'dynamic-reference-rhs-rebind': b"<?php\nclass DynamicReferenceRhsRebind18 {}\n$object = new DynamicReferenceRhsRebind18();\n$rhs = 7;\n$anchor =& $rhs;\n$replacement = 9;\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    $GLOBALS['rhs'] =& $GLOBALS['replacement'];\n    $GLOBALS['anchor'] = 11;\n    return true;\n});\necho ($object->x = $rhs), '|', $object->x, '|', $rhs, '|', $anchor, '|done';\n",
    'dynamic-plain-rhs-promoted-reference': b"<?php\nclass DynamicPlainRhsPromotedReference18 {}\n$object = new DynamicPlainRhsPromotedReference18();\n$rhs = 7;\n$replacement = 9;\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    $GLOBALS['rhs'] =& $GLOBALS['replacement'];\n    return true;\n});\necho ($object->x = $rhs), '|', $object->x, '|', $rhs, '|';\n$replacement = 13;\necho $object->x, '/', $rhs, '|done';\n",
    'dynamic-handler-throw-live': b"<?php\nclass DynamicThrowProbe16 {}\n$object = new DynamicThrowProbe16();\nset_error_handler(function ($level, $message, $file, $line) {\n    echo 'warning|';\n    throw new Exception('stop');\n});\ntry {\n    $object->x = 7;\n    echo 'returned|';\n} catch (Exception $error) {\n    echo isset($object->x) ? 'inserted|' : 'absent|';\n}\necho 'done';\n",
    'dynamic-handler-retires-destination': b"<?php\nclass DynamicRetirementProbe16 {\n    public function __destruct() { echo 'drop|'; }\n}\n$object = new DynamicRetirementProbe16();\nset_error_handler(function ($level, $message, $file, $line) {\n    echo 'warning|';\n    unset($GLOBALS['object']);\n    echo 'released|';\n    return true;\n});\ntry {\n    $object->x = 7;\n    echo 'returned|';\n} catch (Error $error) {\n    echo 'error|';\n}\necho 'done';\n",
    'dynamic-handler-retires-and-throws': b"<?php\nclass DynamicRetiredThrow18 { public function __destruct() { echo 'drop|'; } }\n$object = new DynamicRetiredThrow18();\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|'; unset($GLOBALS['object']); echo 'released|';\n    throw new Exception('stop');\n});\ntry { $object->x = 7; echo 'returned|'; }\ncatch (Exception $error) { echo $error->getMessage(), '|'; }\ncatch (Error $error) { echo 'replacement|'; }\necho 'done';\n",
    'dynamic-computed-receiver': b"<?php\nclass DynamicComputedReceiver18 { public function __destruct() { echo 'drop|'; } }\n$object = new DynamicComputedReceiver18();\nfunction selected_receiver18() { return $GLOBALS['object']; }\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|'; unset($GLOBALS['object']); echo 'released|'; return true;\n});\nselected_receiver18()->x = 7;\necho 'done';\n",
    'dynamic-promoted-rhs-used-result': b"<?php\nclass DynamicPlainRhsPromotedReference18 {}\n$object = new DynamicPlainRhsPromotedReference18();\n$rhs = 7;\n$replacement = 9;\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    $GLOBALS['rhs'] =& $GLOBALS['replacement'];\n    return true;\n});\n$assigned = ($object->x = $rhs);\necho $assigned, '|', $object->x, '|', $rhs, '|';\n$replacement = 13;\necho $assigned, '/', $object->x, '/', $rhs, '|done';\n",
    'dynamic-duplicate-latest-write-unset': b"<?php\nclass DynamicDuplicateLatestWriteUnset18 {}\n$object = new DynamicDuplicateLatestWriteUnset18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\n$object->x = 9;\nforeach ($object as $key => $value) {\n    echo $key, '=', $value, '|';\n}\nunset($object->x);\nforeach ($object as $key => $value) {\n    echo $key, '=', $value, '|';\n}\necho $object->x, '|done';\n",
    'dynamic-retired-receiver-resurrects': b"<?php\nclass DynamicRetiredReceiverResurrects18 {\n    public function __destruct() {\n        echo 'drop|';\n        $GLOBALS['revived'] = $this;\n    }\n}\n$object = new DynamicRetiredReceiverResurrects18();\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    unset($GLOBALS['object']);\n    echo 'released|';\n    return true;\n});\ntry {\n    $object->x = 7;\n    echo 'returned|';\n} catch (Error $error) {\n    echo 'error|';\n}\necho isset($revived->x) ? 'inserted|' : 'absent|';\necho 'done';\n",
    'dynamic-retired-receiver-resurrects-pending': b"<?php\nclass DynamicRetiredReceiverResurrectsPending18 {\n    public function __destruct() {\n        echo 'drop|';\n        $GLOBALS['revived'] = $this;\n    }\n}\n$object = new DynamicRetiredReceiverResurrectsPending18();\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    unset($GLOBALS['object']);\n    echo 'released|';\n    throw new Exception('stop');\n});\ntry {\n    $object->x = 7;\n    echo 'returned|';\n} catch (Exception $error) {\n    echo $error->getMessage(), '|';\n} catch (Error $error) {\n    echo 'replacement|';\n}\necho isset($revived->x) ? 'inserted|' : 'absent|';\necho 'done';\n",
    'dynamic-unused-computed-receiver-rhs-cleanup': b"<?php\nclass DynamicUnusedComputedReceiverCleanup18 {\n    public function __destruct() {\n        echo 'receiver|';\n        unset($this->x);\n        echo 'receiver-end|';\n    }\n}\nclass DynamicUnusedComputedRhsCleanup18 {\n    public function __destruct() { echo 'rhs|'; }\n}\nfunction selected_cleanup_receiver18() { return new DynamicUnusedComputedReceiverCleanup18(); }\nfunction selected_cleanup_rhs18() { return new DynamicUnusedComputedRhsCleanup18(); }\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    return true;\n});\nselected_cleanup_receiver18()->x = selected_cleanup_rhs18();\necho 'done';\n",
    'dynamic-used-computed-receiver-rhs-cleanup': b"<?php\nclass DynamicUnusedComputedReceiverCleanup18 {\n    public function __destruct() {\n        echo 'receiver|';\n        unset($this->x);\n        echo 'receiver-end|';\n    }\n}\nclass DynamicUnusedComputedRhsCleanup18 {\n    public function __destruct() { echo 'rhs|'; }\n}\nfunction selected_cleanup_receiver18() { return new DynamicUnusedComputedReceiverCleanup18(); }\nfunction selected_cleanup_rhs18() { return new DynamicUnusedComputedRhsCleanup18(); }\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    return true;\n});\n$assigned = (selected_cleanup_receiver18()->x = selected_cleanup_rhs18());\necho 'retained|';\nunset($assigned);\necho 'done';\n",
    'dynamic-warning-gc-protected-resurrection': b"<?php\nclass DynamicWarningGcProtectedResurrection18 {\n    public function __destruct() {\n        echo 'drop|';\n        $GLOBALS['revived'] = $this;\n    }\n}\n$object = new DynamicWarningGcProtectedResurrection18();\n$weak = WeakReference::create($object);\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    unset($GLOBALS['object']);\n    echo $GLOBALS['weak']->get() !== null ? 'held|' : 'gone|';\n    echo gc_collect_cycles(), '|';\n    return true;\n});\ntry {\n    $object->x = 7;\n    echo 'returned|';\n} catch (Error $error) {\n    echo 'error|';\n}\necho isset($revived->x) ? 'inserted|' : 'absent|';\necho $weak->get() === $revived ? 'same|' : 'different|';\necho 'done';\n",
    'dynamic-reentry-reference-foreach': b"<?php\nclass DynamicReentryReferenceForeach18 {}\n$object = new DynamicReentryReferenceForeach18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\nforeach ($object as $key => &$value) {\n    echo $key, '=', $value, '|';\n    $value = $value + 10;\n}\nunset($value);\nforeach ($object as $key => $value) {\n    echo $key, '=', $value, '|';\n}\necho $object->x, '|done';\n",
    'duplicate-reference-foreach-escaped-first18': b"<?php\nclass DuplicateReferenceForeachEscapedFirst18 {}\n$object = new DuplicateReferenceForeachEscapedFirst18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\n$first = null;\n$index = 0;\nforeach ($object as $key => &$value) {\n    if ($index === 0) { $first =& $value; }\n    $index = $index + 1;\n}\nunset($value);\necho $first, '/', $object->x, '|';\n$object->x = 9;\necho $first, '/', $object->x, '|';\n$first = 12;\nforeach ($object as $key => $value) { echo $key, '=', $value, '|'; }\nunset($object->x);\necho $first, '/', $object->x, '|';\n$first = 14;\necho $object->x, '|done';\n",
    'duplicate-reference-foreach-delete-next18': b"<?php\nclass DuplicateReferenceForeachDeleteNext18 {}\n$object = new DuplicateReferenceForeachDeleteNext18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\n$first = null;\n$index = 0;\nforeach ($object as $key => &$value) {\n    echo $key, '=', $value, '|';\n    if ($index === 0) {\n        $first =& $value;\n        unset($object->x);\n        $value = 12;\n    }\n    $index = $index + 1;\n}\nunset($value);\necho $index, '/', $first, '/', $object->x, '|done';\n",
    'duplicate-reference-foreach-binding-destructor18': b"<?php\nclass DuplicateReferenceForeachBindingObject18 {}\nclass DuplicateReferenceForeachBindingDestructor18 {\n    public function __destruct() {\n        echo 'drop|';\n        unset($GLOBALS['object']->x);\n        unset($GLOBALS['object']->x);\n    }\n}\n$object = new DuplicateReferenceForeachBindingObject18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\n$value = new DuplicateReferenceForeachBindingDestructor18();\nforeach ($object as $key => &$value) {\n    echo $key, '=', $value, '|';\n    $value = 12;\n}\necho $value, '/';\necho isset($object->x) ? 'present|' : 'absent|';\nunset($value);\necho 'done';\n",
    'duplicate-reference-foreach-readonly18': b"<?php\nclass DuplicateReferenceForeachReadonly18 {\n    public readonly int $locked;\n    public function __construct() { $this->locked = 3; }\n}\n$object = new DuplicateReferenceForeachReadonly18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\ntry {\n    foreach ($object as $key => &$value) { echo 'unexpected|'; }\n} catch (Error $error) {\n    echo 'readonly|';\n}\nforeach ($object as $key => $value) { echo $key, '=', $value, '|'; }\necho 'done';\n",
    'duplicate-reference-foreach-typed-setter18': b"<?php\nclass DuplicateReferenceForeachTypedSetter18 {\n    public protected(set) int $sealed = 3;\n}\n$object = new DuplicateReferenceForeachTypedSetter18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\nforeach ($object as $key => &$value) {\n    if ($key === 'sealed') {\n        try { $value = 'bad'; } catch (TypeError $error) { echo 'typed|'; }\n    }\n    $value = $value + 10;\n}\nunset($value);\nforeach ($object as $key => $value) { echo $key, '=', $value, '|'; }\necho $object->sealed, '/', $object->x, '|done';\n",
}
EXPECTED = {
    'dynamic-reentry-table': 'warning|x=2|x=7|7|done',
    'dynamic-borrowed-rhs': 'warning|9|9|9|done',
    'dynamic-computed-rhs': 'warning|7|7|9|done',
    'dynamic-reference-rhs-rebind': 'warning|11|11|9|11|done',
    'dynamic-plain-rhs-promoted-reference': 'warning|9|9|9|13/13|done',
    'dynamic-handler-throw-live': 'warning|inserted|done',
    'dynamic-handler-retires-destination': 'warning|released|drop|error|done',
    'dynamic-handler-retires-and-throws': 'warning|released|drop|stop|done',
    'dynamic-computed-receiver': 'warning|released|drop|done',
    'dynamic-promoted-rhs-used-result': 'warning|9|9|9|9/13/13|done',
    'dynamic-duplicate-latest-write-unset': 'warning|x=2|x=9|x=2|2|done',
    'dynamic-retired-receiver-resurrects': 'warning|released|drop|error|absent|done',
    'dynamic-retired-receiver-resurrects-pending': 'warning|released|drop|stop|absent|done',
    'dynamic-unused-computed-receiver-rhs-cleanup': 'warning|receiver|rhs|receiver-end|done',
    'dynamic-used-computed-receiver-rhs-cleanup': 'warning|receiver|receiver-end|retained|rhs|done',
    'dynamic-warning-gc-protected-resurrection': 'warning|held|0|drop|error|absent|same|done',
    'dynamic-reentry-reference-foreach': 'warning|x=2|x=7|x=12|x=17|17|done',
    'duplicate-reference-foreach-escaped-first18': 'warning|2/7|2/9|x=12|x=9|12/12|14|done',
    'duplicate-reference-foreach-delete-next18': 'warning|x=2|1/12/12|done',
    'duplicate-reference-foreach-binding-destructor18': 'warning|drop|x=2|12/absent|done',
    'duplicate-reference-foreach-readonly18': 'warning|readonly|locked=3|x=2|x=7|done',
    'duplicate-reference-foreach-typed-setter18': 'warning|typed|sealed=13|x=12|x=17|13/17|done',
}
BOUNDARIES = {
    'dynamic-handler-exit-shutdown': (
        b"<?php\nclass DynamicHandlerExitShutdown18 {}\n$object = new DynamicHandlerExitShutdown18();\nregister_shutdown_function(function() use ($object) {\n    echo isset($object->x) ? 'inserted|' : 'absent|';\n});\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    exit(0);\n});\n$object->x = 7;\necho 'unreachable|';\n",
        'dynamic property warning exit continuation'),
    'dynamic-reentry-cast': (
        b"<?php\nclass DynamicReentryCast18 {}\n$object = new DynamicReentryCast18();\nset_error_handler(function($level, $message, $file, $line) use ($object) {\n    echo 'warning|';\n    @$object->x = 2;\n    return true;\n});\n$object->x = 7;\n$array = (array) $object;\nforeach ($array as $key => $value) {\n    echo $key, '=', $value, '|';\n}\necho $array['x'], '|done';\n",
        'array cast of duplicate dynamic property buckets'),
    'dynamic-plain-rhs-unset': (
        b"<?php\nclass DynamicPlainRhsUnset18 {}\n$object = new DynamicPlainRhsUnset18();\n$rhs = 7;\nset_error_handler(function($level, $message, $file, $line) {\n    echo 'warning|';\n    unset($GLOBALS['rhs']);\n    return true;\n});\n$object->x = $rhs;\nrestore_error_handler();\necho isset($object->x) ? 'set|' : 'unset|';\nforeach ($object as $key => $value) {\n    echo $key, '=', $value, '|';\n}\necho 'done';\n",
        'dynamic property warning RHS pointer lifetime or undefined CV'),
}


def prepare(directory, source):
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], directory/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], directory/'adapter')
        parsed = frontend.request({'op':'parse', 'source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op':'check', 'ast':parsed['ast'], 'fixture':True})
        assert checked['ok'] is True
        (directory/'program.watsup').write_text(checked['fixture']+'\n')
        return {'frontend':'accepted', 'checked':'program', 'model_evaluations':0}
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()


def boundary(directory, source, reason):
    result = cross.invoke.process([str(ROOT/'bin/php-semantics'), str(source),
        '--steps', '100000', '--timeout', '60'], directory/'model', 90, directory)
    assert result.returncode == 1 and not result.stderr
    outcome = json.loads(result.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == 'unsupported' and outcome['reason'] == reason
    assert outcome['exit_status'] is None and outcome['diagnostic'] is None
    assert base64.b64decode(outcome['stdout'], validate=True) == b'warning|'
    assert not base64.b64decode(outcome['stderr'], validate=True)
    return {'status':outcome['status'], 'reason':reason, 'agreement_claim':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare','source','boundary'])
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    candidates = BOUNDARIES if args.mode=='boundary' else CASES
    if args.mode=='prepare': candidates = CASES | BOUNDARIES
    selected = args.select.split(',') if args.select else list(candidates)
    assert selected and len(selected)==len(set(selected)) and all(name in candidates for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='dynamic-property-warning-'+args.mode+'-', dir=ROOT/'.tools'))
    report = {'mode':args.mode, 'before':before, 'profile':cross.invoke.types.PROFILE,
              'jobs':1, 'caps':{'native':30,'model_cli':60,'process':90},
              'passed':False, 'completed':False, 'records':[]}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out/name; directory.mkdir()
            original = CASES[name] if name in CASES else BOUNDARIES[name][0]
            source = directory/'source.php'; source.write_bytes(original)
            row = {'case':name, 'source_sha256':cross.invoke.sha(source), 'completed':False}
            report['records'].append(row)
            if args.mode=='prepare': row['outcome'] = prepare(directory, source)
            elif args.mode=='boundary': row['outcome'] = boundary(directory, source, BOUNDARIES[name][1])
            else: row['outcome'] = cross.source(
                {'abrupt':False, 'expected_exit_status':0, 'expected_stdout':EXPECTED[name]}, directory, source)
            assert cross.snapshot(None)==before
            assert source.read_bytes()==original
            row['completed']=True
            print(name, row['outcome'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure']={'type':type(error).__name__, 'message':str(error)}
        raise
    finally:
        report['after']=cross.snapshot(None)
        report['passed']=report['passed'] and report['before']==report['after']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__=='__main__':
    main()
