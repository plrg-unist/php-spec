"""Prepare only the current outer-array copy/cache/static-reference fixture."""
import warning_consumer_prepare as prep
import warning_consumer_current_run as current

prep.SOURCES, prep.CASES = current.run.SOURCES, current.run.CASES
prep.inputs = current.inputs

if __name__ == '__main__':
    raise SystemExit(0 if prep.main() else 1)
