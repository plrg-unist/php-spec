"""Parse/check and compile only the fixed missing-reference state witnesses."""
import warning_consumer_prepare as family
from warning_reference_cases import CASES as SOURCES
from warning_reference_protocol import CASES, PREFIX
from warning_reference_run import configure, inputs


def main():
    configure()
    family.SOURCES = SOURCES
    family.CASES = CASES
    family.PREFIX = PREFIX
    family.inputs = inputs
    return family.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
