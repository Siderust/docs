#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Portable entry point. Scientific records are read-only; every run writes separate outputs."""
import argparse
import csv
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from verify import ARTICLE, digest, verify

ROOT = Path(__file__).resolve().parent


def preserved():
    files = {}
    for group in ('terrestrial', 'lunar', 'results'):
        for path in (ARTICLE/f'experiments/{group}/recorded').iterdir():
            if path.is_file():
                if path.name in files and digest(path) != digest(files[path.name]):
                    raise RuntimeError(f'Ambiguous recorded filename: {path.name}')
                files[path.name] = path
    return files


class Execution:
    def __init__(self, path, record='commands.json'):
        self.path = path
        self.record = record
        self.commands = []
        (path/'logs').mkdir(exist_ok=True)

    def run(self, command, name, *, output=None, cwd=ARTICLE):
        command = list(map(str, command))
        print(f'[{name}]', flush=True)
        self.commands.append({'command': command, 'cwd': str(cwd), 'log': f'logs/{name}.log'})
        (self.path/self.record).write_text(json.dumps(self.commands, indent=2)+'\n')
        log = self.path/f'logs/{name}.log'
        with log.open('w') as stderr:
            if output:
                with output.open('w') as stdout:
                    status = subprocess.run(command, cwd=cwd, stdout=stdout, stderr=stderr)
            else:
                status = subprocess.run(command, cwd=cwd, stdout=stderr, stderr=subprocess.STDOUT)
        if status.returncode:
            raise RuntimeError(f'{name} failed ({status.returncode}); see {log}')
        return log


def environment(execution):
    import erfa
    import numpy
    import spiceypy
    import platform
    versions = dict(python=platform.python_version(), numpy=numpy.__version__,
                    pyerfa=erfa.__version__, erfa=erfa.version.erfa_version,
                    spiceypy=spiceypy.__version__, cspice=spiceypy.tkvrsn('TOOLKIT'))
    expected = dict(python='3.12.13', numpy='2.5.4', pyerfa='2.0.1.5', erfa='2.0.1',
                    spiceypy='6.0.0', cspice='CSPICE_N0067')
    if versions != expected or not __debug__:
        raise RuntimeError(f'Incorrect scientific environment: {versions}')
    (execution.path/'environment.json').write_text(json.dumps(versions, indent=2)+'\n')
    return versions


def rust_environment(execution):
    import tomllib
    cargo = ['cargo', '+1.93.1']
    execution.run(cargo+['--version'], 'cargo-version')
    execution.run(['rustc', '+1.93.1', '-Vv'], 'rustc-version')
    if not (execution.path/'logs/rustc-version.log').read_text().startswith('rustc 1.93.1 '):
        raise RuntimeError('Rust 1.93.1 is required')
    graphs = []
    for project in (ARTICLE/'examples', ROOT/'runner', ROOT/'controls'):
        lock = tomllib.loads((project/'Cargo.lock').read_text())
        graphs.append(sorted((p['name'], p['version'], p['source'], p.get('checksum'),
                              tuple(p.get('dependencies', [])))
                             for p in lock['package'] if 'source' in p))
    if not graphs[0] == graphs[1] == graphs[2] or len(graphs[0]) != 92:
        raise RuntimeError('The evaluated registry dependency graphs differ')
    execution.run(cargo+['tree', '--locked', '--manifest-path', ARTICLE/'examples/Cargo.toml'], 'cargo-tree')


def applications(execution, data, kernels):
    cargo = ['cargo', '+1.93.1', 'run', '--locked', '--quiet', '--manifest-path', ARTICLE/'examples/Cargo.toml']
    def app(binary, args=(), output=None):
        execution.run(cargo+['--bin', binary, '--', *args], binary, output=output)
    # Check a small orientation subset independently before the daily grid.
    app('viewing', [data/'representative', '--representative'])
    execution.run([sys.executable, ARTICLE/'scripts/validate_antares.py', '--data', data/'representative',
                   '--catalog', ARTICLE/'experiments/terrestrial/catalog.json', '--representative'], 'representative-reference')
    app('viewing', [data])
    app('viewing_events', [data])
    app('historical_feasibility', output=data/'historical-feasibility.csv')
    app('antares_diagnostics', output=data/'sidereal-diagnostics.csv')
    app('lunar_geometry', [kernels/'de440s.bsp', data])
    app('earth_from_moon', [kernels/'de440s.bsp'], output=data/'lunar-example.txt')
    rendered = re.fullmatch(r'altitude=(\S+) °, azimuth=(\S+) °, range=(\S+) km\n',
                            (data/'lunar-example.txt').read_text())
    if rendered is None or list(map(float, rendered.groups())) != list(map(float, (data/'lunar.txt').read_text().split())):
        raise RuntimeError('Lunar example and application quantities differ')
    execution.run([sys.executable, ARTICLE/'scripts/validate_antares.py', '--data', data,
                   '--catalog', ARTICLE/'experiments/terrestrial/catalog.json'], 'antares-reference')
    execution.run([sys.executable, ARTICLE/'scripts/validate_lunar_application.py', '--data', data,
                   '--kernels', kernels, '--inputs', ARTICLE/'experiments/lunar/inputs.json'], 'lunar-reference')


def core(execution, data, kernels):
    from check_controls import check
    from fetch_sources import fetch
    cargo = ['cargo', '+1.93.1', 'run', '--release', '--locked', '--quiet',
             '--manifest-path', ROOT/'runner/Cargo.toml']
    execution.run(cargo+['--bin', 'siderust-paper-revalidation', '--', kernels/'de440s.bsp'],
                  'ephemeris', output=data/'ephemeris.csv')
    execution.run([sys.executable, ROOT/'reference/extended.py', '--prepare'], 'boundary-prepare')
    execution.run(cargo+['--bin', 'validation', '--', data], 'validation')
    execution.run(cargo+['--bin', 'runtime_controls'], 'runtime-controls', output=data/'runtime-controls.log')
    if (data/'runtime-controls.log').read_text().strip() != 'All runtime controls passed':
        raise RuntimeError('Runtime contract result missing')
    execution.run(cargo+['--bin', 'coverage', '--', kernels/'de440s.bsp'], 'coverage', output=data/'coverage.log')
    lines = (data/'coverage.log').read_text().splitlines()
    if len(lines) != 6 or [('Ok(' in line) for line in lines] != [False, False, True, True, False, False]:
        raise RuntimeError('Unexpected converted-TT coverage outcomes')
    check(data)
    execution.run([sys.executable, ROOT/'reference/ephemeris.py'], 'ephemeris-reference')
    execution.run([sys.executable, ROOT/'reference/extended.py'], 'extended-reference')
    sources = fetch(execution.path/'sources')
    os.environ['SIDERUST_BSP_PATH'] = str(kernels/'de440s.bsp')
    # Include the real-kernel frame test, which upstream normally ignores.
    testsets = [
        ('eop-tests', sources['tempoch'], ['-p', 'tempoch-core', 'earth::eop::tests'], [10]),
        ('frame-tests', sources['siderust'], ['--test', 'ephemeris_frame_consistency', '--', '--include-ignored'], [11]),
        ('spk-surface-tests', sources['siderust'], ['--test', 'test_spk_runtime', '--test', 'body_surface_horizontal'], [36, 11]),
    ]
    counts = {}
    for name, source, args, expected in testsets:
        log = execution.run(['cargo', '+1.93.1', 'test', '--locked', '--manifest-path', source/'Cargo.toml', *args], name, cwd=source)
        text = log.read_text()
        populations = [int(n) for n in re.findall(r'test result: ok\. (\d+) passed;', text) if int(n)]
        if populations != expected or re.search(r'; [1-9]\d* ignored;', text):
            raise RuntimeError(f'{name}: unexpected regression populations {populations}')
        counts[name] = populations
    return counts


def compare(data, full):
    original = preserved()
    # Machine metadata and timing-dependent test logs are provenance only.
    names = [p.name for group in ('terrestrial', 'lunar')
             for p in (ARTICLE/f'experiments/{group}/recorded').iterdir()
             if p.suffix in ('.csv', '.json') or p.name == 'lunar.txt']
    if full:
        names += [p.name for p in (ROOT/'recorded').iterdir() if p.suffix in ('.csv', '.json')]
        names += ['coverage.log', 'runtime-controls.log']
    comparisons = {}
    for name in sorted(set(names)):
        fresh = data/name
        if not fresh.is_file():
            raise RuntimeError(f'Required fresh scientific output is missing: {name}')
        if name == 'extended-residuals.csv':
            # The original record predates the application reference's placement
            # in this export: it orders the same residuals differently and uses
            # LF rather than csv.writer's CRLF. Compare exact keyed fields, with
            # no numeric tolerance and no discarded or duplicate cases.
            def keyed(path):
                with path.open(newline='') as stream:
                    rows = list(csv.reader(stream))
                values = {tuple(row[:2]): row[2:] for row in rows[1:]}
                if len(values) != len(rows)-1:
                    raise RuntimeError(f'Duplicate residual case in {path}')
                return rows[0], values
            equal = keyed(fresh) == keyed(original[name])
            method = 'exact CSV fields keyed by (observable, case); row order and line endings ignored'
        elif fresh.suffix == '.json':
            equal = json.loads(fresh.read_text()) == json.loads(original[name].read_text())
            method = 'parsed JSON identity'
        else:
            equal = fresh.read_bytes() == original[name].read_bytes()
            method = 'byte identity'
        comparisons[name] = method if equal else 'DIFFERENT'
    (data.parent/'evidence-comparison.json').write_text(json.dumps(comparisons, indent=2)+'\n')
    different = [name for name, result in comparisons.items() if result == 'DIFFERENT']
    if different:
        raise RuntimeError('Fresh evidence differs from publication: '+', '.join(different))
    return comparisons


def worker(mode, path, supplied_kernels):
    from regenerate import generate
    execution = Execution(path)
    versions = environment(execution)
    data = path/'data'
    data.mkdir()
    records = preserved()
    details = {'mode': mode, 'versions': versions}
    if mode == 'tables':
        for name, source in records.items():
            shutil.copyfile(source, data/name)
    else:
        rust_environment(execution)
        kernels = supplied_kernels or path/'kernels'
        execution.run([sys.executable, ARTICLE/'scripts/fetch_application_kernels.py', '--inputs',
                       ARTICLE/'experiments/lunar/inputs.json', '--destination', kernels], 'kernel-inputs')
        os.environ['REPRO_OUTPUT'] = str(data)
        os.environ['REPRO_KERNELS'] = str(kernels)
        applications(execution, data, kernels)
        if mode == 'full':
            details['upstream_regressions'] = core(execution, data, kernels)
        details['evidence_comparisons'] = compare(data, mode == 'full')
        if mode == 'applications':
            for name in ('summary.json', 'extended-summary.json', 'controls-summary.json'):
                shutil.copyfile(records[name], data/name)
            details['table_core_data'] = 'preserved evidence; core experiments not executed in applications mode'
        execution.run(['cargo', '+1.93.1', 'check', '--locked', '--manifest-path', ARTICLE/'examples/Cargo.toml', '--bins'], 'article-examples')
        execution.run(['cargo', '+1.93.1', 'run', '--locked', '--quiet', '--manifest-path', ARTICLE/'examples/Cargo.toml', '--bin', 'surface_contract'], 'surface-contract')
    details['generated_publication_outputs'] = generate(data, path/'generated')
    (path/'verification.json').write_text(json.dumps(details, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--mode', choices=('applications', 'full', 'tables'), default='applications')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('run_id')
    parser.add_argument('kernels', nargs='?', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.mode, Path(args.run_id), args.kernels)
        return
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.run_id):
        parser.error('Run identifiers may contain only letters, digits, underscores and hyphens')
    verify()
    path = ARTICLE/'experiments/runs'/args.run_id
    if path.exists():
        parser.error(f'Refusing to overwrite existing run: {path}')
    if args.mode == 'tables' and args.kernels:
        parser.error('Tables mode does not use kernels')
    kernels = args.kernels.resolve() if args.kernels else None
    path.mkdir(parents=True)
    report = dict(status='running', mode=args.mode, started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  publication_files_verified=True)
    # Clear inherited optimization/profile settings and keep fresh builds in the run.
    for key in list(os.environ):
        if key.startswith(('CARGO_PROFILE_', 'CARGO_TARGET_')) or key in (
            'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_BUILD_TARGET', 'PYTHONPATH',
            'PYTHONHOME', 'PYTHONOPTIMIZE', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER'):
            del os.environ[key]
    os.environ['CARGO_TARGET_DIR'] = str(path/'target')
    os.environ['PYTHONNOUSERSITE'] = '1'
    execution = Execution(path, record='bootstrap-commands.json')
    try:
        execution.run(['uv', 'venv', '--python', '3.12.13', path/'pyenv'], 'python-environment')
        python = path/'pyenv/bin/python'
        execution.run(['uv', 'pip', 'install', '--python', python, '--require-hashes',
                       '-r', ARTICLE/'experiments/requirements.lock'], 'python-dependencies')
        execution.run([python, Path(__file__).resolve(), '--worker', '--mode', args.mode, path,
                       *([kernels] if kernels else [])], 'scientific-workflow')
        verify()
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        raise
    finally:
        report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (path/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'{args.mode} replay passed: {path}/report.json')


if __name__ == '__main__':
    main()
