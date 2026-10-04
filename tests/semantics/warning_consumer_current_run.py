"""Compare the one current cache/static-prior source and reached copy state."""
import warning_consumer_run as run
import warning_consumer_current as current

BASE_INPUTS = run.inputs
ROOT = run.ROOT


def inputs():
    result = BASE_INPUTS()
    for name in ('warning_consumer_current.php', 'warning_consumer_current.py',
                 'warning_consumer_current_prepare.py', 'warning_consumer_current_run.py'):
        path = ROOT / 'tests/semantics' / name
        result[str(path)] = run.describe(path)
    return result


run.inputs = inputs
run.SOURCES, run.CASES = current.SOURCES, current.CASES
run.SOURCE_CAP, run.FINITE_CAP = 150, 330

if __name__ == '__main__':
    raise SystemExit(0 if run.main() else 1)
