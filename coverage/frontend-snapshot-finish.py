"""Finalize this bounded validation snapshot after its recorded checks pass."""
import hashlib,itertools,json,shutil,subprocess,sys
from pathlib import Path
R=Path.cwd();audit=json.loads((R/'.tools/review3-snapshot.json').read_text());S=Path(audit['snapshot'])
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def protected(name):
    if name.startswith(('frontend/','adapter/','native/','vendor/php-parser/','scripts/')): return True
    if name.startswith('tests/') and not name.startswith('tests/semantics/'): return True
    if name.startswith('spec/') and not name.startswith('spec/semantics/'): return True
    return name in {'Makefile','dune-project','bin/php-syntax','coverage/encoding-spellings.json','.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe','spec/semantics/11-source-occurrences.watsup','spec/semantics/21-source-context.watsup','tests/semantics/source_context.py','tests/semantics/source_occurrences.py','tests/semantics/static_types.py'}
required={name:digest for name,digest in audit['files'].items() if protected(name)}
for name,digest in required.items():
    assert sha(R/name)==sha(S/name)==digest,('syntax input changed',name)
# An added syntax input cannot escape the stored-file comparison.
for root in ('frontend','adapter','native','vendor/php-parser','scripts','tests','spec'):
    for path in (R/root).rglob('*'):
        name=str(path.relative_to(R))
        if path.is_file() and not {'__pycache__','_build'}.intersection(path.parts) and path.suffix!='.pyc' and protected(name):
            assert name in required,('new syntax input',name)
cmd=[sys.executable,'-c','import sys,json,hashlib;sys.path.insert(0,"tests");from corpus import inputs;rows=list(inputs());print(json.dumps({"records":len(rows),"sha256":hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}))']
for root in (R,S):
    observed=json.loads(subprocess.check_output(cmd,cwd=root,text=True));assert observed==audit['corpus'],('corpus changed',root,observed)
fp=json.loads(subprocess.check_output([sys.executable,'-c','import sys,json;sys.path.insert(0,"tests");import validate;print(json.dumps(validate.implementation_fingerprint()))'],cwd=S,text=True));assert fp==audit['fingerprint']
summaries={}
for kind in ('targeted','generated','deep','corpus'):
    summary=json.loads((S/f'coverage/results-{kind}.summary.json').read_text())
    assert summary['stable_implementation'] and summary['implementation']==fp
    assert sum(summary['counts'].values())==summary['tested']
    assert not set(summary['counts']).difference({'pass','parser_rejection','compile_phase_difference','redirect_container','non_source','invalid_program_roundtrip_difference'})
    summaries[kind]=summary
assert summaries['corpus']['tested']==audit['corpus']['records'] and summaries['corpus']['shards']==4
assert len(summaries['corpus']['nodes'])==169
sys.path.insert(0,str(R/'tests'))
from corpus import inputs
membership=0
with (S/'coverage/results-corpus.jsonl').open() as stream:
    for original,line in itertools.zip_longest(inputs(),stream):
        assert original is not None and line is not None,'missing or extra corpus record'
        row=json.loads(line)
        for key in ('id','origin','section','ini','ini_b64','sha256','bytes'):
            assert original.get(key)==row.get(key),('corpus record changed',original['id'],key)
        if original['status']!='source': assert original['status']==row['status']
        membership+=1
assert membership==audit['corpus']['records']
# Retain original full rows locally under the existing generated-results policy.
artifacts={}
for kind in summaries:
    old=S/f'coverage/results-{kind}.jsonl';new=R/f'coverage/results-frontend-syntax-{kind}.jsonl';shutil.copy2(old,new)
    artifacts[str(new.relative_to(R))]={'sha256':sha(new),'bytes':new.stat().st_size}
for name in ('frontend-snapshot-test.log','frontend-snapshot-corpus.log','frontend-snapshot-inventory.log'):
    shutil.copy2(S/'coverage'/name,R/'coverage'/name);artifacts['coverage/'+name]={'sha256':sha(R/'coverage'/name),'bytes':(R/'coverage'/name).stat().st_size}
for name in ('grammar.json','scanner.json','grammar-mapping.json','scanner-mapping.json'):
    shutil.copy2(S/'coverage'/name,R/'coverage'/name)
    artifacts['coverage/'+name]={'sha256':sha(R/'coverage'/name),'bytes':(R/'coverage'/name).stat().st_size}
report={'scope':'complete syntax validation of copied candidate inputs; no semantic, rebuild or portability claim','snapshot_audit':audit,'summaries':summaries,'syntax_equality':{'result':'pass','files':required,'corpus':audit['corpus']},'artifacts':artifacts,'commands':[{'command':'make -o build test','exit_status':0},{'command':'python3 tests/parallel_validate.py --corpus --lint-all --output coverage/results-corpus.jsonl','exit_status':0},{'command':'python3 tests/grammar_coverage.py && python3 scripts/grammar-mapping.py && python3 scripts/scanner-mapping.py && python3 scripts/encoding-spellings.py','exit_status':0}],'finalization_script':{'path':'coverage/frontend-snapshot-finish.py','sha256':sha(Path(__file__))},'accepted_commit':'9658958c','ordered_corpus_membership':{'result':'pass','records':membership,'retained_fields':['id','origin','section','ini','ini_b64','sha256','bytes'],'non_source_classifications_preserved':True},'inventory_counts':{'grammar_productions':635,'witnessed_productions':631,'disposition_productions':[0,71,149,200],'constructors':169,'scanner_actions':191,'token_character_alternatives':264,'encoding_spellings':214,'encoding_lookup_checks':685}}
(R/'coverage/frontend-syntax-repair.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'syntax_files_equal':len(required),'corpus':summaries['corpus']['counts'],'records':summaries['corpus']['tested'],'fingerprint':fp['sha256']}))
