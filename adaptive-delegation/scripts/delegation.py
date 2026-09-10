#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Stage-wise local delegation records; never launch agents or contact a server."""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import stat
import sys
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeAlias, cast

from jsonschema import Draft202012Validator

JSON: TypeAlias = str | int | float | bool | None | list['JSON'] | dict[str, 'JSON']
Object: TypeAlias = dict[str, JSON]
START = '<!-- adaptive-delegation:records:v1 -->'
END = '<!-- /adaptive-delegation:records:v1 -->'
TERMINAL = {'completed', 'failed', 'cancelled'}
INPUTS = {'prepare': 'prepare_input', 'record-direct': 'record_direct_input',
          'record-run': 'record_run_input', 'assess': 'assess_input'}
CREATE_COMMANDS = {'prepare', 'record-direct'}
SCHEMA = json.loads((Path(__file__).resolve().parents[1] / 'schemas' / 'record.schema.json').read_text(encoding='utf-8'))


class RecordError(Exception):
    """Invalid input or an unsafe local update; no silent repair is attempted."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def new_id(prefix: str) -> str:
    return prefix + uuid.uuid4().hex


def object_value(value: JSON) -> Object:
    if not isinstance(value, dict):
        raise RecordError('Expected a JSON object.')
    return value


def objects(value: JSON) -> list[Object]:
    if not isinstance(value, list):
        raise RecordError('Expected a JSON array.')
    return [object_value(item) for item in value]


def decode_json(text: str) -> Object:
    def pairs(items: list[tuple[str, JSON]]) -> Object:
        result: Object = {}
        for key, value in items:
            if key in result:
                raise RecordError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result

    def invalid_constant(value: str) -> None:
        raise RecordError(f'Non-finite JSON number: {value}')

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except json.JSONDecodeError as error:
        raise RecordError(f'Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}') from error
    return object_value(value)


def validate(value: JSON, definition: str) -> None:
    # Validate the supported schema without downloading any schemas or references.
    validator = Draft202012Validator({'$ref': f'#/$defs/{definition}', '$defs': SCHEMA['$defs']})
    errors = sorted(validator.iter_errors(value), key=lambda e: str(list(e.absolute_path)))
    if errors:
        error = errors[0]
        location = '.'.join(str(part) for part in error.absolute_path) or definition
        raise RecordError(f'{location}: {error.message}')

    def finite(item: JSON) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise RecordError('Numbers must be finite.')
        if isinstance(item, dict):
            for child in item.values():
                finite(child)
        elif isinstance(item, list):
            for child in item:
                finite(child)
    finite(value)


def metric_invariants(metrics: Object) -> None:
    incoming = metrics.get('input_tokens')
    if metrics.get('input_token_scope') == 'includes_cache' and incoming is not None:
        for key in ('cache_read_tokens', 'cache_write_tokens'):
            cached = metrics.get(key)
            if cached is not None and cast(int, cached) > cast(int, incoming):
                raise RecordError(f'{key} cannot exceed input_tokens with includes_cache.')
    if metrics.get('cost_amount') is not None:
        if not metrics.get('cost_currency') or not metrics.get('cost_basis'):
            raise RecordError('cost_amount requires cost_currency and cost_basis.')


def validate_record(record: Object) -> None:
    validate(record, 'record')
    for key in ('created_at', 'updated_at'):
        try:
            datetime.strptime(str(record[key]), '%Y-%m-%dT%H:%M:%SZ')
        except ValueError as error:
            raise RecordError(f'Invalid {key}.') from error
    attempt_ids: set[str] = set()
    for attempt in objects(record['attempts']):
        aid = str(attempt['attempt_id'])
        if aid in attempt_ids:
            raise RecordError('Duplicate attempt_id within a record.')
        if 'retry_of' in attempt and str(attempt['retry_of']) not in attempt_ids:
            raise RecordError('retry_of must identify an earlier attempt in this record.')
        attempt_ids.add(aid)
        metric_invariants(object_value(attempt['metrics']))
    review = record.get('delegation_assessment')
    if review is not None and not set(cast(list[str], object_value(review)['attempt_ids'])) <= attempt_ids:
        raise RecordError('Delegation assessment refers to an unknown attempt.')


def cache_ratio(metrics: Object) -> float | None:
    incoming = metrics.get('input_tokens')
    read = metrics.get('cache_read_tokens')
    if incoming is None or read is None:
        return None
    if metrics.get('input_token_scope') == 'includes_cache':
        total = cast(int, incoming)
    elif metrics.get('input_token_scope') == 'excludes_cache' and metrics.get('cache_write_tokens') is not None:
        total = cast(int, incoming) + cast(int, read) + cast(int, metrics['cache_write_tokens'])
    else:
        return None
    return cast(int, read) / total if total else None


def summary(record: Object) -> Object:
    attempts = objects(record['attempts'])
    mode = record.get('execution_mode', 'delegate')
    review = record.get('delegation_assessment')
    review_pending = mode == 'delegate' and (review is None or
        object_value(review)['attempt_ids'] != [a['attempt_id'] for a in attempts] or
        any(a['execution_status'] not in TERMINAL for a in attempts))
    return {
        'record_id': record['record_id'], 'revision': record['revision'],
        'execution_mode': mode,
        'delegation_review_pending': review_pending,
        'task_type': object_value(record['task'])['type'], 'attempts': len(attempts),
        'unassessed_attempts': sum(a['assessment'] is None for a in attempts),
        'nonterminal_attempts': sum(a['execution_status'] not in TERMINAL for a in attempts),
        'pending_use_attempts': sum(a['assessment'] is not None and object_value(a['assessment'])['output_use'] == 'pending' for a in attempts),
        'awaiting_run': mode == 'delegate' and not attempts,
    }


@dataclass
class Document:
    """One tool-managed JSONL block, with all surrounding Markdown preserved."""
    before: str
    after: str
    records: list[Object]
    newline: str = '\n'
    has_block: bool = False

    @classmethod
    def parse(cls, raw: bytes | None) -> Document:
        text = (raw or b'').decode('utf-8')
        newline = '\r\n' if '\r\n' in text else '\n'
        starts = list(re.finditer(r'^' + re.escape(START) + r'\r?$', text, re.M))
        ends = list(re.finditer(r'^' + re.escape(END) + r'\r?$', text, re.M))
        if any(line.startswith(('<!-- adaptive-delegation:records:', '<!-- /adaptive-delegation:records:')) and line not in (START, END) for line in (part.removesuffix('\r') for part in text.split('\n'))):
            raise RecordError('Unsupported or malformed managed-block marker; no automatic migration.')
        if not starts and not ends:
            return cls(text, '', [], newline)
        if len(starts) != 1 or len(ends) != 1 or starts[0].end() >= ends[0].start():
            raise RecordError('Malformed or duplicate managed record markers; file not modified.')
        lines = text[starts[0].end():ends[0].start()].strip().split('\n')
        lines = [line.removesuffix('\r') for line in lines]
        if len(lines) < 2 or lines[0] != '```jsonl' or lines[-1] != '```':
            raise RecordError('Managed block must contain one jsonl fence.')
        records = [decode_json(line) for line in lines[1:-1] if line.strip()]
        seen: set[str] = set()
        for record in records:
            validate_record(record)
            rid = str(record['record_id'])
            if rid in seen:
                raise RecordError(f'Duplicate record_id: {rid}')
            seen.add(rid)
        end = ends[0].end()
        if text[end - 1:end] == '\r':
            end -= 1  # Keep the original end-marker newline in the untouched suffix.
        return cls(text[:starts[0].start()], text[end:], records, newline, True)

    def render(self) -> bytes:
        before = self.before
        if not self.has_block:
            before = before or '# Project Delegation Experience\n\n## Current Hints\n\n'
            if not before.endswith(('\n', '\r')):
                before += self.newline
            if not before.endswith(self.newline * 2):
                before += self.newline
        lines = [START, '```jsonl']
        lines.extend(json.dumps(r, ensure_ascii=False, allow_nan=False, separators=(',', ':')) for r in self.records)
        lines += ['```', END]
        if not self.has_block:
            lines.append('')
        return (before + self.newline.join(lines) + self.after).encode('utf-8')

    def find(self, record_id: str) -> Object:
        for record in self.records:
            if record['record_id'] == record_id:
                return record
        raise RecordError(f'Unknown record_id: {record_id}')


def read_bytes(path: Path) -> bytes | None:
    if path.is_symlink():
        raise RecordError(f'Refusing a symlink record/export file: {path}')
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


@contextmanager
def locked(path: Path) -> Iterator[None]:
    """Serialize cooperating recorder writes; stale locks need manual inspection."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + '.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise RecordError(f'Busy lock: {lock}. Retry after its owner exits; inspect stale locks manually.') from error
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(f'pid={os.getpid()}\n')
        yield
    finally:
        lock.unlink()


def atomic_write(path: Path, content: bytes, expected: bytes | None) -> bool:
    """Replace one local file, preserving its mode; refuse observed outside edits."""
    if read_bytes(path) != expected:
        raise RecordError(f'File changed during update: {path}')
    if expected == content:
        return False
    mode = stat.S_IMODE(path.stat().st_mode) if expected is not None else 0o600
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    temp = Path(name)
    try:
        os.chmod(temp, mode)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if read_bytes(path) != expected:
            raise RecordError(f'File changed during update: {path}')
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return True


def create_record(document: Document, data: Object, project_name: str, *, direct: bool = False) -> Object:
    validate(data, 'record_direct_input' if direct else 'prepare_input')
    if not direct and not data.get('requested_child_model'):
        raise RecordError('requested_child_model must be known before recording a planned delegation.')
    timestamp = now()
    record: Object = {
        'format': 'adaptive-delegation/staged-record', 'schema_version': 1,
        'record_id': new_id('D'), 'revision': 1, 'created_at': timestamp, 'updated_at': timestamp,
        'execution_mode': 'direct' if direct else 'delegate',
        'project_name': data.get('project_name') or project_name,
        'parent': {'model': data.get('parent_model'), 'effort': data.get('parent_effort')},
        'task': {'description': data['task_description'], 'type': data['task_type'],
                 'domains': data.get('task_domains', []), 'estimated_difficulty': data.get('estimated_difficulty')},
        'attempts': [], 'parent_metrics': {},
    }
    if direct:
        record['direct_reason'] = data['direct_reason']
    else:
        record['requested_child'] = {'model': data['requested_child_model'], 'effort': data.get('requested_child_effort'),
                                     'context': data.get('requested_context')}
        record['model_selection_reason'] = data.get('model_selection_reason', 'unknown')
        record['expected_delegation_benefit'] = data['expected_delegation_benefit']
    for key in ('workspace_task', 'group_id', 'host', 'skill_revision'):
        if key in data:
            record[key] = data[key]
    validate_record(record)
    document.records.append(record)
    return {'record_id': record['record_id'], 'revision': 1}


def select_attempt(record: Object, attempt_id: str | None, run_id: JSON) -> Object | None:
    attempts = objects(record['attempts'])
    if attempt_id:
        matches = [a for a in attempts if a['attempt_id'] == attempt_id]
        if not matches:
            raise RecordError(f'Unknown attempt_id: {attempt_id}')
        return matches[0]
    if run_id is not None:
        matches = [a for a in attempts if a['run_id'] == run_id]
        if len(matches) > 1:
            raise RecordError('Native run ID has multiple continuations; specify --attempt-id.')
        return matches[0] if matches else None
    if len(attempts) > 1:
        raise RecordError('Multiple attempts: specify --attempt-id or --run-id.')
    return attempts[0] if attempts else None


def record_run(record: Object, data: Object, args: argparse.Namespace) -> Object:
    validate(data, 'record_run_input')
    if record.get('execution_mode') == 'direct':
        raise RecordError('A direct choice has no child runs; prepare a separate delegation if the choice changes.')
    if not data:
        raise RecordError('record-run needs at least one reported field.')
    if args.new_attempt and args.attempt_id:
        raise RecordError('--new-attempt cannot be combined with --attempt-id.')
    attempt = None if args.new_attempt else select_attempt(record, args.attempt_id, data.get('run_id'))
    if attempt is None and not args.new_attempt and data.get('run_id') is not None and any(a['run_id'] is None for a in objects(record['attempts'])):
        raise RecordError('An attempt has no native ID; bind it with --attempt-id or start --new-attempt.')
    if attempt is None:
        attempt = {'attempt_id': new_id('A'), 'run_id': data.get('run_id'), 'execution_status': 'unknown',
                   'child': {'model': None, 'effort': None, 'context': None},
                   'metrics': {'input_token_scope': 'unknown', 'missing_metrics_reason': 'not_collected'}, 'assessment': None}
        attempt['requested_child'] = (copy.deepcopy(record['requested_child']) if not record['attempts']
                                      else {'model': None, 'effort': None, 'context': None})
        if args.retry_of:
            attempt['retry_of'] = args.retry_of
        cast(list[JSON], record['attempts']).append(attempt)
    elif args.retry_of:
        raise RecordError('--retry-of is only valid for a new attempt.')
    if data.get('run_id') is not None and attempt['run_id'] not in (None, data['run_id']):
        raise RecordError('Cannot change an existing native run_id; add a new attempt.')
    old_status = str(attempt['execution_status'])
    new_status = str(data.get('execution_status', old_status))
    if old_status in TERMINAL and new_status != old_status:
        raise RecordError('Do not reopen a terminal attempt; use --new-attempt (optionally --retry-of).')
    for key in ('run_id', 'execution_status'):
        if key in data:
            if key == 'run_id' and data[key] is None and attempt[key] is not None:
                raise RecordError('Cannot clear a known native run_id.')
            attempt[key] = data[key]
    child = object_value(attempt['child'])
    for key in ('model', 'effort', 'context'):
        input_key = 'child_' + key if key != 'context' else 'context'
        if input_key in data:
            child[key] = data[input_key]
    requested = object_value(attempt['requested_child'])
    for key, input_key in [('model', 'requested_child_model'), ('effort', 'requested_child_effort'), ('context', 'requested_context')]:
        if input_key in data:
            requested[key] = data[input_key]
    metrics = object_value(attempt['metrics'])
    for key in SCHEMA['$defs']['metrics']['properties']:
        if key in data:
            metrics[key] = data[key]
    return {'attempt_id': attempt['attempt_id'], 'run_id': attempt['run_id']}


def replace_assessment(owner: Object, key: str, proposed: Object, reason: str | None) -> bool:
    """Retain earlier parent judgments without counting repeated reports twice."""
    current = owner.get(key)
    previous = object_value(current) if current is not None else None
    if previous is not None and {k: v for k, v in previous.items() if k != 'assessed_at'} == proposed:
        return False
    if previous is not None:
        if not reason:
            raise RecordError('Changing an assessment requires --correction-reason; previous evidence is retained.')
        validate(reason, 'note')
        history = cast(list[JSON], owner.setdefault(key + '_history', []))
        history.append({'at': now(), 'previous': copy.deepcopy(previous), 'reason': reason})
    owner[key] = {**proposed, 'assessed_at': now()}
    return True


def assess(record: Object, data: Object, args: argparse.Namespace) -> Object:
    validate(data, 'assess_input')
    if record.get('execution_mode') == 'direct':
        raise RecordError('A direct choice has no child output or delegation usefulness to assess.')
    attempts = objects(record['attempts'])
    if not attempts:
        raise RecordError('No matching attempt. Record the result or launch failure first.')
    response: Object = {}
    if 'output_quality' in data:
        attempt = select_attempt(record, args.attempt_id, args.run_id)
        if attempt is None:
            raise RecordError('No matching attempt.')
        if args.run_id is not None and attempt['run_id'] != args.run_id:
            raise RecordError('--attempt-id and --run-id identify different attempts.')
        current = attempt['assessment']
        proposed: Object = {'output_quality': data['output_quality'], 'output_use': data['output_use']}
        if 'note' in data:
            proposed['note'] = data['note']
        elif current is not None and 'note' in object_value(current):
            proposed['note'] = object_value(current)['note']
        changed = replace_assessment(attempt, 'assessment', proposed, args.correction_reason)
        # An output correction can change utility; preserve the old judgment for review.
        if changed and 'delegation_usefulness' not in data and record.get('delegation_assessment') is not None:
            history = cast(list[JSON], record.setdefault('delegation_assessment_history', []))
            history.append({'at': now(), 'previous': record['delegation_assessment'],
                            'reason': 'Output assessment changed; reconsider whole-delegation usefulness.'})
            record['delegation_assessment'] = None
        response['attempt_id'] = attempt['attempt_id']
    elif args.attempt_id or args.run_id:
        raise RecordError('Delegation usefulness covers the whole record; omit attempt/run selectors without output verdicts.')
    if 'delegation_usefulness' in data:
        if data['delegation_usefulness'] != 'unknown' and any(a['execution_status'] not in TERMINAL for a in attempts):
            raise RecordError('Nonterminal attempts: leave delegation usefulness unknown until the result is observable.')
        proposed = {'delegation_usefulness': data['delegation_usefulness'],
                    'attempt_ids': [a['attempt_id'] for a in attempts]}
        previous = record.get('delegation_assessment')
        reason = args.correction_reason
        if previous is not None and object_value(previous)['attempt_ids'] != proposed['attempt_ids'] and not reason:
            reason = 'Reassessed after additional attempts, including their cost and parent burden.'
        replace_assessment(record, 'delegation_assessment', proposed, reason)
    parent = object_value(record['parent_metrics'])
    for key in SCHEMA['$defs']['parent_metrics']['properties']:
        if key in data:
            parent[key] = data[key]
    return response


def export_records(document: Document, destination: Path, ids: list[str] | None) -> Object:
    records = [document.find(rid) for rid in dict.fromkeys(ids)] if ids else document.records
    destination.mkdir(parents=True, exist_ok=True)
    changed = 0
    # Each JSON file is atomic. A failed multi-file write can be resumed safely.
    with locked(destination / '.delegation-export'):
        plan: list[tuple[Path, bytes, bytes | None]] = []
        for record in records:
            validate_record(record)
            target = destination / f"{record['record_id']}.json"
            raw = read_bytes(target)
            if raw is not None:
                previous = decode_json(raw.decode('utf-8'))
                validate_record(previous)
                identity = ('format', 'schema_version', 'record_id', 'project_name', 'created_at')
                if any(previous[k] != record[k] for k in identity):
                    raise RecordError(f'Export identity conflict: {target.name}')
                if previous['revision'] > record['revision'] or (previous['revision'] == record['revision'] and previous != record):
                    raise RecordError(f'Export revision conflict: {target.name}; reconcile rather than overwrite.')
            content = (json.dumps(record, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')
            plan.append((target, content, raw))
        for target, content, raw in plan:
            changed += atomic_write(target, content, raw)
    return {'exported': len(records), 'files_changed': changed,
            'unassessed_attempts': sum(cast(int, summary(r)['unassessed_attempts']) for r in records),
            'awaiting_run': sum(bool(summary(r)['awaiting_run']) for r in records),
            'direct_records': sum(r.get('execution_mode') == 'direct' for r in records),
            'delegation_reviews_pending': sum(bool(summary(r)['delegation_review_pending']) for r in records)}


def resolved(field: dict[str, object]) -> dict[str, object]:
    while '$ref' in field:
        target = SCHEMA
        for part in str(field['$ref']).removeprefix('#/').split('/'):
            target = target[part]
        field = target
    return field


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    root.add_argument('--project-root', type=Path, help='Explicit project root; required for record operations.')
    root.add_argument('--record-file', type=Path, default=Path('.agents/delegation.md'), help='Path relative to project root, or an explicitly approved absolute override.')
    subs = root.add_subparsers(dest='command', required=True)
    for command, definition in INPUTS.items():
        sub = subs.add_parser(command, allow_abbrev=False, help={'prepare':'Save pre-run task, delegation purpose, and requested settings.', 'record-direct':'Record a representative choice not to delegate.', 'record-run':'Merge reported runtime facts.', 'assess':'Assess child output and whole-delegation usefulness.'}[command])
        if command not in CREATE_COMMANDS:
            sub.add_argument('record_id')
            sub.add_argument('--attempt-id', help='Internal attempt ID; otherwise use run ID or the sole attempt.')
        sub.add_argument('--json', type=Path, metavar='FILE', help='Flat stage input JSON; - reads stdin. Flags may add distinct fields, never silently override.')
        if command == 'record-run':
            sub.add_argument('--new-attempt', action='store_true', help='Create another attempt when no new native run ID is available.')
            sub.add_argument('--retry-of', help='Internal attempt ID being retried; only for a new attempt.')
        if command == 'assess':
            sub.add_argument('--run-id', help='Native run ID to assess.')
            sub.add_argument('--correction-reason', help='Short reason required when changing an existing assessment.')
        required = SCHEMA['$defs'][definition].get('required', [])
        for key, spec in SCHEMA['$defs'][definition]['properties'].items():
            field = resolved(spec)
            help_text = field.get('description', '') + (' [required]' if key in required else '')
            kwargs: dict[str, object] = {'default': argparse.SUPPRESS, 'help': help_text}
            if 'enum' in field:
                kwargs['choices'] = [v for v in field['enum'] if v is not None]
            else:
                field_type = field.get('type')
                if isinstance(field_type, list):
                    field_type = next(t for t in field_type if t != 'null')
                if field_type in ('integer', 'number'):
                    kwargs['type'] = int if field_type == 'integer' else float
                elif field_type == 'array':
                    kwargs['nargs'] = '+'
            sub.add_argument('--' + key.replace('_', '-'), **kwargs)
    for name, help_text in [('show','Inspect selected records, or list short summaries.'), ('validate','Validate managed records without requiring complete metrics.')]:
        sub = subs.add_parser(name, help=help_text, allow_abbrev=False)
        sub.add_argument('record_ids', nargs='*')
    sub = subs.add_parser('export', help='Write local JSON exports. No Git, network, or private-data scanning.', allow_abbrev=False)
    sub.add_argument('--destination', type=Path, required=True, help='Approved local output directory; use a new-format subdirectory.')
    sub.add_argument('--record-id', dest='record_ids', action='append')
    sub = subs.add_parser('schema', help='Print the canonical JSON Schema or a stage-input schema.', allow_abbrev=False)
    sub.add_argument('stage', nargs='?', choices=['record', *INPUTS], default='record')
    return root


def stage_data(args: argparse.Namespace) -> Object:
    data: Object = {}
    if args.json is not None:
        text = sys.stdin.read() if str(args.json) == '-' else args.json.read_text(encoding='utf-8')
        data = decode_json(text)
    for key in SCHEMA['$defs'][INPUTS[args.command]]['properties']:
        if key in vars(args):
            if key in data:
                raise RecordError(f'{key} provided in both JSON and flags.')
            data[key] = vars(args)[key]
    return data


def execute(args: argparse.Namespace) -> Object:
    if args.command == 'schema':
        definition = INPUTS.get(args.stage, 'record')
        return cast(Object, {'$schema': SCHEMA['$schema'], '$ref': f'#/$defs/{definition}', '$defs': SCHEMA['$defs']})
    if args.project_root is None or not args.project_root.is_dir():
        raise RecordError('Supply --project-root pointing to the existing project directory.')
    root = args.project_root.resolve()
    path = args.record_file if args.record_file.is_absolute() else root / args.record_file
    if args.command in INPUTS:
        data = stage_data(args)
        validate(data, INPUTS[args.command])
        with locked(path):
            original = read_bytes(path)
            document = Document.parse(original)
            if args.command in CREATE_COMMANDS:
                response = create_record(document, data, root.name, direct=args.command == 'record-direct')
                record = document.find(str(response['record_id']))
                changed = True
            else:
                record = document.find(args.record_id)
                previous = copy.deepcopy(record)
                response = record_run(record, data, args) if args.command == 'record-run' else assess(record, data, args)
                changed = record != previous
                if changed:
                    record['revision'] = cast(int, record['revision']) + 1
                    record['updated_at'] = now()
            validate_record(record)
            if changed:
                atomic_write(path, document.render(), original)
            return {'ok': True, 'saved': True, 'changed': changed, **summary(record), **response}
    original = read_bytes(path)
    if original is None:
        raise RecordError(f'Record file does not exist: {path}')
    document = Document.parse(original)
    if args.command == 'export':
        return {'ok': True, **export_records(document, args.destination, args.record_ids)}
    records = [document.find(rid) for rid in args.record_ids] if args.record_ids else document.records
    if args.command == 'show' and args.record_ids:
        return {'ok': True, 'records': cast(JSON, records), 'derived_cache_read_ratios': cast(JSON, [
            {'attempt_id': a['attempt_id'], 'ratio': cache_ratio(object_value(a['metrics']))}
            for r in records for a in objects(r['attempts'])])}
    return {'ok': True, 'managed_records': len(records), 'records': cast(JSON, [summary(r) for r in records]),
            'note': 'Only tool-managed blocks are counted; legacy prose is not imported.'}


def main(argv: list[str] | None = None) -> int:
    try:
        response = execute(parser().parse_args(argv))
        print(json.dumps(response, ensure_ascii=False, allow_nan=False, separators=(',', ':')))
        return 0
    except (RecordError, OSError, UnicodeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
