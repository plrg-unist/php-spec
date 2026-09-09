#!/usr/bin/env python3
"""Check or provision pinned read-only references before private semantics gates."""
import argparse,hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
# Direct oracle-source dependencies of the current semantics harnesses. Extend
# this list when a harness adds a reference; full syntax/corpus uses the full tree.
REFERENCES=[f'vendor/php-src/Zend/{name}' for name in (
    'zend_compile.c','zend_API.c','zend_ast.c','zend_operators.c',
    'zend_hash.c','zend_gc.c','zend_inheritance.c','zend_vm_def.h',
    'zend_variables.c','zend_execute.c','zend_language_parser.y',
    'zend_language_scanner.l')]+['vendor/php-src/main/php_variables.c']


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(target,copy_missing=False):
    target=target.resolve()
    if target==ROOT.resolve():raise ValueError('private root must differ from the canonical checkout')
    if not (target/'spec/semantics/modules.json').is_file():raise ValueError('private root is missing spec/semantics/modules.json')
    expected={name:digest(ROOT/name) for name in REFERENCES}
    missing=[name for name in REFERENCES if not (target/name).is_file()]
    mismatched=[name for name in REFERENCES if (target/name).is_file() and digest(target/name)!=expected[name]]
    if mismatched:raise ValueError('read-only oracle reference mismatch; refusing overwrite: '+', '.join(mismatched))
    if missing and not copy_missing:raise ValueError('private semantics references missing: '+', '.join(missing)+'; provision before freezing with --copy-missing')
    manifest={'scope':'Read-only oracle references for semantics harnesses; does not provision tools, implementation, full syntax corpus or a source-closure claim.','references':expected}
    output=target/'semantics-reference-inputs.json'
    if output.exists() and json.loads(output.read_text())!=manifest:raise ValueError('existing reference manifest differs; preserve it and use a new private root')
    for name in missing:
        path=target/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,path)
    if {name:digest(target/name) for name in REFERENCES}!=expected:raise ValueError('reference bytes changed while provisioning')
    if not output.exists():output.write_text(json.dumps(manifest,indent=2)+'\n')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--copy-missing',action='store_true',help='copy missing canonical references before the private root is frozen; never overwrite mismatches')
    args=parser.parse_args()
    try:output=prepare(args.root,args.copy_missing)
    except (ValueError,OSError) as error:parser.exit(1,str(error)+'\n')
    print(f'Private semantics references: {len(REFERENCES)} exact files; {output}')


if __name__=='__main__':main()
