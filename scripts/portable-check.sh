#!/usr/bin/env bash
# Linux audit: fresh sources, no Git metadata, hidden workspace/cache, no network.
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
audit_dir=$(mktemp -d /var/tmp/php-spec-portable.XXXXXX)
namespace_env=(PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
  OPAMROOTISOK=1 JOBS=1 DUNE_JOBS=1)
python3 - "$project_dir" "$audit_dir" "${namespace_env[@]}" <<'SEAL'
import hashlib, json, stat, sys
from pathlib import Path
root=Path(sys.argv[1]); inputs=Path(sys.argv[2])/'.tools/portable-inputs'
inputs.mkdir(parents=True)
def vector(names):
    paths=[root/name for name in names]
    assert all(path.resolve().is_relative_to(root) for path in paths), 'escaping original input'
    return {str(path.relative_to(root)): {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'mode': stat.S_IMODE(path.stat().st_mode)} for path in sorted(set(paths))}
roots=('frontend','adapter','spec','native','tests','scripts','bin','vendor/php-parser')
names=[str(path.relative_to(root)) for name in roots for path in (root/name).rglob('*')
       if path.is_file() and not {'__pycache__','_build'}.intersection(path.relative_to(root).parts)
       and path.suffix!='.pyc']+['Makefile','dune-project']
seals={'source-vector.json': vector(names), 'immutable-archives.json': vector((
    'coverage/semantics/comparison-phase-originals.json','coverage/semantics/comparison-overflow-draft-disagreement.json')),
    'initial-inventory.json': vector('coverage/'+name for name in
    ('encoding-spellings.json','grammar.json','scanner.json','grammar-mapping.json','scanner-mapping.json'))}
for name,value in seals.items():
    (inputs/name).write_text(json.dumps(value,indent=2)+'\n')
launch={'supplied_unshare_argv': ['sudo','unshare','--mount','--net','--pid','--fork',
        '--mount-proc','--kill-child','/bin/bash','-s','--',str(inputs.parent.parent),*sys.argv[3:]],
        'supplied_env_i_argv': ['env','-i',*sys.argv[3:],'python3','-'],
        'supplied_unshare_cwd': str(Path.cwd()), 'supplied_env_i_cwd': str(inputs.parent.parent)}
(inputs/'namespace-launch.json').write_text(json.dumps(launch,indent=2)+'\n')
SEAL
tar -C "$project_dir" --exclude='./.git' --exclude='./.tools' \
  --exclude='./_build' --exclude='./tests/semantics/_build' --exclude='./build' \
  -cf - . | tar -C "$audit_dir" -xf -
printf 'Portable checkout: %s\n' "$audit_dir"
sudo unshare --mount --net --pid --fork --mount-proc --kill-child /bin/bash -s -- "$audit_dir" "${namespace_env[@]}" <<'AUDIT'
set -euo pipefail
mount --make-rprivate /
mount -t tmpfs tmpfs /home
mount -t tmpfs tmpfs /tmp
cd "$1"
shift
exec env -i "$@" python3 - <<'PHASES'
import hashlib, json, os, shutil, signal, stat, subprocess, sys, time
from pathlib import Path

root = Path.cwd()
raw = root / '.tools/portable-raw'
raw.mkdir(parents=True)
phases = [{'id': 'verify-imports-before', 'command': ['python3', 'scripts/verify-inputs.py'], 'cap_seconds': 300}, {'id': 'vendored-bootstrap', 'command': ['scripts/build-deps.sh'], 'cap_seconds': 7200}, {'id': 'fresh-adapter-and-native-helpers', 'command': ['make', 'build'], 'cap_seconds': 600}, {'id': 'fresh-nested-numeric', 'command': ['scripts/opam-exec.sh', 'dune', 'build', '--root', 'tests/semantics', '-j', '1', 'numeric_runner.exe'], 'cap_seconds': 600}, {'id': 'existing-syntax-tests', 'command': ['make', 'test'], 'cap_seconds': 3600}, {'id': 'full-classified-syntax', 'command': ['python3', 'tests/parallel_validate.py', '--corpus', '--lint-all', '--jobs', '1', '--output', 'coverage/results-corpus.jsonl'], 'cap_seconds': 18000}, {'id': 'current-inventory', 'command': ['make', 'inventory'], 'cap_seconds': 3600}, {'id': 'retained-native-source30', 'command': ['python3', 'tests/semantics/method_runtime.py', '--catalogue', 'tests/semantics/compiler_publication_cases.json'], 'cap_seconds': 1800}, {'id': 'source-derived-history6', 'command': ['python3', 'tests/semantics/compiler_publication_protocol.py'], 'cap_seconds': 750}, {'id': 'checked-main-modifier26', 'command': ['python3', 'tests/semantics/compiler_method_modifier_guards.py'], 'cap_seconds': 180}, {'id': 'verify-imports-after', 'command': ['python3', 'scripts/verify-inputs.py'], 'cap_seconds': 300}]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
report = {'result': 'preflight', 'phases': [], 'conditional_unrun': [p['id'] for p in phases]}
save = lambda: (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
save()

def vector(names):
    paths = [root / name for name in names]
    assert all(path.resolve().is_relative_to(root) for path in paths), 'escaping input'
    return {str(path.relative_to(root)): {'sha256': sha(path), 'mode': stat.S_IMODE(path.stat().st_mode)}
            for path in sorted(set(paths))}

def source_vector():
    roots = ('frontend', 'adapter', 'spec', 'native', 'tests', 'scripts', 'bin', 'vendor/php-parser')
    names = [str(path.relative_to(root)) for name in roots for path in (root / name).rglob('*')
             if path.is_file() and not {'__pycache__', '_build'}.intersection(path.relative_to(root).parts)
             and path.suffix != '.pyc'] + ['Makefile', 'dune-project']
    return vector(names)

def live_children():
    rows = []
    for path in Path('/proc').iterdir():
        if path.name.isdecimal() and int(path.name) != os.getpid():
            try:
                fields = (path / 'stat').read_text().rpartition(') ')[2].split()
                if fields[0] not in ('Z', 'X'):
                    rows.append({'pid': int(path.name), 'pgid': int(fields[2]),
                                 'argv': [os.fsdecode(arg) for arg in (path / 'cmdline').read_bytes().split(b'\0') if arg]})
            except (FileNotFoundError, ProcessLookupError):
                pass
    return rows

inventory_names = tuple('coverage/' + name for name in
    ('encoding-spellings.json', 'grammar.json', 'scanner.json', 'grammar-mapping.json', 'scanner-mapping.json'))
try:
    inputs = root / '.tools/portable-inputs'
    entry = json.loads((inputs / 'source-vector.json').read_text())
    archives = json.loads((inputs / 'immutable-archives.json').read_text())
    inventory = json.loads((inputs / 'initial-inventory.json').read_text())
    namespace_launch = json.loads((inputs / 'namespace-launch.json').read_text())
    assert source_vector() == entry, 'copied source differs from original seal'
    assert vector(archives) == archives, 'copied immutable archives differ from original seal'
    assert vector(inventory_names) == inventory, 'copied inventory differs from original seal'
    namespace = {'pid': os.getpid(), 'namespaces': {name: os.readlink('/proc/self/ns/' + name)
                 for name in ('mnt', 'net', 'pid')}, 'mountinfo': Path('/proc/self/mountinfo').read_text(),
                 'network_interfaces': Path('/proc/net/dev').read_text(), 'environment': dict(os.environ),
                 'no_git': not (root / '.git').exists(), 'initial_tools': sorted(path.name for path in (root / '.tools').iterdir())}
    (raw / 'namespace.json').write_text(json.dumps(namespace, indent=2) + '\n')
    assert namespace['pid'] == 1 and namespace['no_git']
    for item in namespace_launch['supplied_env_i_argv'][2:-2]:
        key, value = item.split('=', 1)
        assert namespace['environment'][key] == value
    assert namespace['initial_tools'] == ['portable-inputs', 'portable-raw']
    assert not (root / '_build').exists() and not (root / 'tests/semantics/_build').exists()
    mounts = {line.split()[4]: line.split(' - ', 1)[1].split()[0]
              for line in namespace['mountinfo'].splitlines()}
    assert mounts.get('/home') == mounts.get('/tmp') == 'tmpfs'
    assert {line.split(':', 1)[0].strip() for line in namespace['network_interfaces'].splitlines()[2:]} == {'lo'}
    report.update(result='running', original_seal_inputs=vector(
        '.tools/portable-inputs/' + name for name in ('source-vector.json', 'immutable-archives.json', 'initial-inventory.json', 'namespace-launch.json')),
        namespace_sha256=sha(raw / 'namespace.json'))
except Exception as error:
    report.update(result='entry_guard_failure', error=repr(error)); save(); raise SystemExit(1)
save()
runtime = None
for index, phase in enumerate(phases):
    directory = raw / phase['id']; directory.mkdir()
    record = dict(phase, cwd=str(root), supplied_argv=phase['command'],
                  supplied_environment=dict(os.environ), result='preparing', exit_status=None, pass_=False)
    record['pass'] = record.pop('pass_')
    report['phases'].append(record)
    persist = lambda: ((directory / 'status.json').write_text(json.dumps(record, indent=2) + '\n'), save())
    persist()
    try:
        assert source_vector() == entry, 'copied source changed'
        assert vector(archives) == archives, 'immutable archives changed'
        assert vector(inventory_names) == inventory, 'inventory changed outside its phase'
        assert not live_children(), 'surviving child before phase'
        if phase['id'] == 'retained-native-source30':
            sys.path.insert(0, str(root / 'tests'))
            import validate
            runtime_names = ('.tools/php/bin/php', '.tools/php-file.so', '.tools/request-clock.so',
                             '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe')
            def runtime_vector():
                return {'fingerprint': validate.implementation_fingerprint(),
                        'runtime_and_inventory_inputs': vector(runtime_names + inventory_names + tuple(archives))}
            runtime = runtime_vector()
            (raw / 'post-inventory-runtime.json').write_text(json.dumps(runtime, indent=2) + '\n')
        if phase['id'] == 'current-inventory':
            preimages = raw / 'inventory-preimages'; preimages.mkdir()
            for name in inventory_names:
                shutil.copy2(root / name, preimages / Path(name).name)
            (preimages / 'manifest.json').write_text(json.dumps(inventory, indent=2) + '\n')
    except Exception as error:
        record.update(result='guard_failure_before_launch', guard_error=repr(error))
        report['result']='stopped_first_failure_or_change'; persist(); raise SystemExit(1)
    started = time.monotonic()
    try:
        with (directory / 'stdout').open('wb') as stdout, (directory / 'stderr').open('wb') as stderr:
            process = subprocess.Popen(record['supplied_argv'], cwd=root, env=record['supplied_environment'],
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            record.update(result='running', pid=process.pid, owned_pgid=process.pid, popen_args=process.args)
            (directory / 'command.json').write_text(json.dumps(record, indent=2) + '\n'); persist()
            try:
                record['exit_status'] = process.wait(timeout=phase['cap_seconds'])
                record['result'] = 'completed'
            except subprocess.TimeoutExpired:
                record['result'] = 'timeout_unknown'
            finally:
                record['live_before_cleanup'] = live_children()
                if process.poll() is None or record['live_before_cleanup']:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                record['cleanup_cap_seconds'] = 5
                try:
                    record['cleanup_exit_status'] = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    record.update(cleanup_exit_status=None, cleanup_timeout_unknown=True)
                record['live_after_cleanup'] = live_children()
    except Exception as error:
        record['producer_error'] = repr(error)
    record['elapsed_seconds'] = time.monotonic() - started
    report['conditional_unrun'] = [p['id'] for p in phases[index + (1 if 'pid' in record else 0):]]
    persist()
    try:
        record.update(stdout_sha256=sha(directory/'stdout'), stderr_sha256=sha(directory/'stderr'),
                      source_unchanged=source_vector()==entry, archives_unchanged=vector(archives)==archives)
        if phase['id'] == 'current-inventory':
            inventory = vector(inventory_names)
            (raw / 'post-inventory-vector.json').write_text(json.dumps(inventory, indent=2) + '\n')
        record['inventory_unchanged'] = vector(inventory_names) == inventory
        record['pass'] = (record['result']=='completed' and record['exit_status']==0
                          and record.get('cleanup_exit_status')==0 and not record.get('cleanup_timeout_unknown')
                          and not record.get('producer_error') and not record['live_before_cleanup']
                          and not record['live_after_cleanup'] and record['source_unchanged']
                          and record['archives_unchanged'] and record['inventory_unchanged'])
        if runtime is not None:
            record['runtime_unchanged'] = runtime_vector() == runtime
            record['pass'] = record['pass'] and record['runtime_unchanged']
    except Exception as error:
        record.update(guard_error=repr(error), **{'pass': False})
    persist()
    print(json.dumps({'phase': phase['id'], 'pass': record['pass']}), flush=True)
    if not record['pass']:
        report['result']='stopped_first_failure_or_change'; save(); raise SystemExit(1)
try:
    report.update(final_source_unchanged=source_vector()==entry,
                  final_archives_unchanged=vector(archives)==archives, live_children=live_children())
    assert report['final_source_unchanged'] and report['final_archives_unchanged'] and not report['live_children']
except Exception as error:
    report.update(result='final_guard_failure', guard_error=repr(error)); save(); raise SystemExit(1)
report['result']='pass'; save()
PHASES
AUDIT
printf 'Portable audit passed: %s\n' "$audit_dir"
