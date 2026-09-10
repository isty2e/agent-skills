"""Local, synthetic contract tests. No agents, credentials, Git or network needed."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'delegation.py'
spec = importlib.util.spec_from_file_location('delegation_tool', SCRIPT)
assert spec is not None and spec.loader is not None
d = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d
spec.loader.exec_module(d)


class DelegationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / '.agents' / 'delegation.md'

    def call(self, *args: str, stdin: str | None = None, error: bool = False) -> dict:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with patch('sys.stdin', io.StringIO(stdin or '')):
                result = d.main(['--project-root', str(self.root), *args])
        self.assertEqual(result, 2 if error else 0, err.getvalue())
        return json.loads(err.getvalue() if error else out.getvalue())

    def prepare(self, **fields: object) -> str:
        data = {'task_description': 'Check a bounded contract.', 'task_type': 'verify',
                'requested_child_model': 'example/worker', 'requested_child_effort': 'high',
                'expected_delegation_benefit': 'save_time'}
        data.update(fields)
        return self.call('prepare', '--json', '-', stdin=json.dumps(data))['record_id']

    def record(self, rid: str) -> dict:
        return self.call('show', rid)['records'][0]

    def start(self, rid: str, *args: str) -> str:
        return self.call('record-run', rid, '--run-id', 'R1', '--execution-status', 'completed', *args)['attempt_id']

    def test_schema_is_valid(self) -> None:
        Draft202012Validator.check_schema(d.SCHEMA)
        for stage in d.INPUTS:
            self.assertIn('$defs', self.call('schema', stage))

    def test_three_stages_and_seconds(self) -> None:
        rid = self.prepare(model_selection_reason='exploration')
        rec = self.record(rid)
        self.assertEqual(rec['attempts'], [])
        self.assertEqual(rec['requested_child']['model'], 'example/worker')
        aid = self.start(rid, '--elapsed-seconds', '92.5', '--input-tokens', '100',
                         '--cache-read-tokens', '60', '--input-token-scope', 'includes_cache')
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is')
        rec = self.record(rid)
        self.assertEqual(rec['attempts'][0]['metrics']['elapsed_seconds'], 92.5)
        self.assertIsNone(rec['attempts'][0]['child']['model'])
        self.assertEqual(rec['attempts'][0]['assessment']['output_use'], 'used_as_is')
        self.assertEqual(self.call('show', rid)['derived_cache_read_ratios'], [{'attempt_id': aid, 'ratio': 0.6}])

    def test_missing_values_are_not_zero_or_elapsed_guesses(self) -> None:
        rid = self.prepare()
        self.start(rid)
        rec = self.record(rid)
        self.assertNotIn('elapsed_seconds', rec['attempts'][0]['metrics'])
        self.assertNotIn('cost_amount', rec['attempts'][0]['metrics'])
        self.assertIsNone(self.call('show', rid)['derived_cache_read_ratios'][0]['ratio'])

    def test_defaults_are_not_model_selections(self) -> None:
        rid = self.prepare()
        self.assertEqual(self.record(rid)['model_selection_reason'], 'unknown')
        self.assertEqual(self.record(rid)['parent'], {'model': None, 'effort': None})

    def test_stage_validation_and_no_partial_save(self) -> None:
        for fields in [{'task_type': 'typo'}, {'task_description': ''}, {'requested_child_model': ''}, {'acceptance_ref': 'bad'}]:
            base={'task_type': 'verify', 'task_description': 'Check', 'requested_child_model': 'example/worker',
                  'expected_delegation_benefit': 'save_time'}
            base.update(fields)
            self.call('prepare', '--json', '-', stdin=json.dumps(base), error=True)
            self.assertFalse(self.file.exists())
        rid=self.prepare(); original=self.file.read_bytes()
        for field,value in [('elapsed_seconds', -1), ('input_tokens', True), ('input_tokens', 1.5), ('input_tokens', -5), ('elapsed_seconds', 1e309), ('typo', 1)]:
            self.call('record-run', rid, '--json', '-', stdin=json.dumps({field:value}), error=True)
            self.assertEqual(self.file.read_bytes(), original)

    def test_duplicate_keys_and_duplicate_input_rejected(self) -> None:
        self.call('prepare', '--json', '-', stdin='{"task_type":"verify","task_type":"review"}', error=True)
        self.call('prepare', '--task-type', 'verify', '--json', '-', stdin='{"task_type":"verify"}', error=True)

    def test_wrong_cache_scope_is_not_guessed(self) -> None:
        rid=self.prepare()
        self.start(rid, '--input-tokens', '20', '--cache-read-tokens', '80')
        self.assertIsNone(self.call('show', rid)['derived_cache_read_ratios'][0]['ratio'])
        original=self.file.read_bytes()
        self.call('record-run', rid, '--input-token-scope', 'includes_cache', error=True)
        self.assertEqual(original,self.file.read_bytes())
        self.call('record-run', rid, '--input-token-scope', 'excludes_cache', '--cache-write-tokens', '0')
        self.assertEqual(self.call('show', rid)['derived_cache_read_ratios'][0]['ratio'],0.8)

    def test_zero_denominator_is_unknown(self) -> None:
        rid=self.prepare()
        self.start(rid,'--input-tokens','0','--cache-read-tokens','0','--input-token-scope','includes_cache')
        self.assertIsNone(self.call('show',rid)['derived_cache_read_ratios'][0]['ratio'])

    def test_cost_needs_currency_and_meaning(self) -> None:
        rid=self.prepare()
        self.call('record-run',rid,'--cost-amount','0.2',error=True)
        self.start(rid,'--cost-amount','0.2','--cost-currency','USD','--cost-basis','unverified_indicator')
        self.assertEqual(self.record(rid)['attempts'][0]['metrics']['cost_basis'],'unverified_indicator')

    def test_repeated_receipt_and_assessment_are_idempotent(self) -> None:
        rid=self.prepare(); self.start(rid,'--output-tokens','10')
        original=self.file.read_bytes()
        self.assertFalse(self.call('record-run',rid,'--run-id','R1','--execution-status','completed','--output-tokens','10')['changed'])
        self.assertEqual(original,self.file.read_bytes())
        flags=('assess',rid,'--output-quality','incomplete','--output-use','used_after_local_fix','--note','One fix.')
        self.call(*flags); original=self.file.read_bytes()
        self.assertFalse(self.call(*flags)['changed'])
        self.assertEqual(original,self.file.read_bytes())

    def test_late_metrics_preserve_assessment(self) -> None:
        rid=self.prepare(); self.start(rid)
        self.call('assess',rid,'--output-quality','incorrect','--output-use','used_after_major_rework')
        assessment=copy.deepcopy(self.record(rid)['attempts'][0]['assessment'])
        self.call('record-run',rid,'--output-tokens','12')
        self.assertEqual(self.record(rid)['attempts'][0]['assessment'],assessment)

    def test_assessment_correction_requires_reason_and_retains_evidence(self) -> None:
        rid=self.prepare(); self.start(rid)
        flags=('assess',rid,'--output-quality','meets_requirements','--output-use','used_as_is')
        self.call(*flags,'--note','Initial check.')
        self.call('assess',rid,'--output-quality','incorrect','--output-use','used_as_is',error=True)
        self.call('assess',rid,'--output-quality','incorrect','--output-use','used_as_is','--correction-reason','Later test failed.')
        attempt=self.record(rid)['attempts'][0]
        self.assertEqual(attempt['assessment']['output_quality'],'incorrect')
        self.assertEqual(attempt['assessment_history'][0]['previous']['output_quality'],'meets_requirements')
        self.assertEqual(attempt['assessment']['note'],'Initial check.')

    def test_failed_run_can_have_useful_output(self) -> None:
        rid=self.prepare(); self.call('record-run',rid,'--execution-status','failed','--missing-metrics-reason','no_exposed_lookup')
        self.call('assess',rid,'--output-quality','incomplete','--output-use','used_as_is')
        self.assertEqual(self.record(rid)['attempts'][0]['execution_status'],'failed')

    def test_launch_failure_without_native_id(self) -> None:
        rid=self.prepare()
        first=self.call('record-run',rid,'--execution-status','failed')['attempt_id']
        self.call('assess',rid,'--attempt-id',first,'--output-quality','no_output','--output-use','no_output')
        self.call('record-run',rid,'--run-id','R2','--execution-status','completed',error=True)
        self.call('record-run',rid,'--new-attempt','--retry-of',first,'--run-id','R2','--execution-status','completed')
        self.assertEqual(len(self.record(rid)['attempts']),2)

    def test_bind_missing_native_id_explicitly(self) -> None:
        rid=self.prepare(); aid=self.call('record-run',rid,'--execution-status','running')['attempt_id']
        self.call('record-run',rid,'--attempt-id',aid,'--run-id','R1','--execution-status','completed')
        self.assertEqual(len(self.record(rid)['attempts']),1)
        self.call('record-run',rid,'--attempt-id',aid,'--json','-',stdin='{"run_id":null}',error=True)

    def test_retries_and_same_native_id_continuations(self) -> None:
        rid=self.prepare(); aid=self.start(rid)
        self.call('record-run',rid,'--execution-status','running',error=True)
        new=self.call('record-run',rid,'--new-attempt','--retry-of',aid,'--run-id','R1','--execution-status','completed','--requested-child-effort','medium')['attempt_id']
        self.assertNotEqual(aid,new)
        self.call('assess',rid,'--run-id','R1','--output-quality','unverified','--output-use','pending',error=True)
        self.call('assess',rid,'--attempt-id',new,'--output-quality','meets_requirements','--output-use','used_as_is')
        self.assertIsNone(self.record(rid)['attempts'][1]['requested_child']['model'])
        self.assertEqual(self.record(rid)['attempts'][1]['requested_child']['effort'],'medium')

    def test_unknown_retry_target_and_selector_conflict(self) -> None:
        rid=self.prepare(); aid=self.start(rid)
        self.call('record-run',rid,'--new-attempt','--retry-of','bogus','--run-id','R2',error=True)
        self.call('assess',rid,'--attempt-id',aid,'--run-id','R2','--output-quality','unverified','--output-use','pending',error=True)
        self.assertEqual(len(self.record(rid)['attempts']),1)

    def test_effective_settings_are_not_requested_settings(self) -> None:
        rid=self.prepare(); self.start(rid,'--child-model','example/fallback','--child-effort','low','--context','fork')
        attempt=self.record(rid)['attempts'][0]
        self.assertEqual(attempt['child']['model'],'example/fallback')
        self.assertEqual(attempt['requested_child']['model'],'example/worker')

    def test_json_stdin_clear_unknown_field_without_erasing_other_values(self) -> None:
        rid=self.prepare(); self.start(rid,'--elapsed-seconds','3','--output-tokens','10')
        self.call('record-run',rid,'--json','-',stdin='{"elapsed_seconds": null, "missing_metrics_reason":"not_attributable"}')
        self.assertEqual(self.record(rid)['attempts'][0]['metrics']['output_tokens'],10)
        self.assertIsNone(self.record(rid)['attempts'][0]['metrics']['elapsed_seconds'])

    def test_human_markdown_is_preserved(self) -> None:
        self.file.parent.mkdir(); human='# Hints\n\nKeep my prose.\n\n## Legacy observations\nunchanged'
        self.file.write_text(human)
        rid=self.prepare()
        self.assertTrue(self.file.read_text().startswith(human))
        text=self.file.read_bytes(); before,managed=text.split(d.START.encode(),1)
        self.file.write_bytes(text+b'\n## Human tail\nKeep this too.\n')
        self.start(rid)
        after=self.file.read_bytes()
        self.assertEqual(after.split(d.START.encode(),1)[0],before)
        self.assertTrue(after.endswith(b'\n## Human tail\nKeep this too.\n'))

    def test_existing_marker_at_start_and_no_trailing_newline(self) -> None:
        rid=self.prepare()
        raw=self.file.read_bytes(); raw=raw[raw.index(d.START.encode()):].rstrip(b'\n')
        self.file.write_bytes(raw); self.start(rid)
        self.assertTrue(self.file.read_bytes().startswith(d.START.encode()))
        self.assertTrue(self.file.read_bytes().endswith(d.END.encode()))

    def test_crlf_and_unicode_line_separator(self) -> None:
        self.file.parent.mkdir(); self.file.write_bytes(b'# Hints\r\nHuman\r\n')
        rid=self.prepare(task_description='Unicode\u2028separator; Korean 한글.')
        self.start(rid)
        self.assertTrue(self.file.read_bytes().startswith(b'# Hints\r\nHuman\r\n'))
        self.assertEqual(self.record(rid)['task']['description'],'Unicode\u2028separator; Korean 한글.')

    def test_malformed_duplicate_and_unknown_blocks_are_rejected(self) -> None:
        self.file.parent.mkdir()
        for text in [d.START+'\n', d.END+'\n', '<!-- adaptive-delegation:records:v99 -->\n', d.START+'\nbad\n'+d.END]:
            self.file.write_text(text); old=self.file.read_bytes()
            self.call('validate',error=True)
            self.assertEqual(old,self.file.read_bytes())
        self.file.unlink(); self.prepare(); text=self.file.read_text(); self.file.write_text(text+text)
        self.call('validate',error=True)

    def test_record_and_export_symlinks_rejected(self) -> None:
        target=self.root/'target'; target.write_text('human')
        self.file.parent.mkdir()
        try: self.file.symlink_to(target)
        except OSError: self.skipTest('Symlinks unavailable')
        self.call('prepare','--task-type','verify','--task-description','x','--requested-child-model','x','--expected-delegation-benefit','save_time',error=True)
        self.assertEqual(target.read_text(),'human')

    def test_lock_contention_fails_without_modifying(self) -> None:
        rid=self.prepare(); original=self.file.read_bytes()
        with d.locked(self.file):
            self.call('record-run',rid,'--execution-status','running',error=True)
        self.assertEqual(original,self.file.read_bytes())
        self.assertFalse(self.file.with_name('delegation.md.lock').exists())

    def test_outside_edit_detected(self) -> None:
        rid=self.prepare(); old=self.file.read_bytes(); self.file.write_bytes(old+b'External edit')
        with self.assertRaises(d.RecordError):
            d.atomic_write(self.file,b'New',old)
        self.assertTrue(self.file.read_bytes().endswith(b'External edit'))

    def test_write_failure_leaves_old_file_and_no_temp(self) -> None:
        self.prepare(); old=self.file.read_bytes()
        with patch.object(d.os,'replace',side_effect=OSError('simulated')):
            with self.assertRaises(OSError): d.atomic_write(self.file,b'New',old)
        self.assertEqual(self.file.read_bytes(),old)
        self.assertEqual(list(self.file.parent.iterdir()),[self.file])

    def test_new_file_private_and_existing_mode_preserved(self) -> None:
        rid=self.prepare()
        if os.name != 'posix': self.skipTest('POSIX mode assertion')
        self.assertEqual(self.file.stat().st_mode & 0o777,0o600)
        self.file.chmod(0o640); self.start(rid)
        self.assertEqual(self.file.stat().st_mode & 0o777,0o640)

    def test_explicit_path_not_cwd(self) -> None:
        dest=self.root/'other'/'hints.md'
        self.call('--record-file',str(dest),'prepare','--task-type','verify','--task-description','x','--requested-child-model','x','--expected-delegation-benefit','save_time')
        self.assertTrue(dest.exists()); self.assertFalse(self.file.exists())

    def test_export_pending_failed_and_assessed_without_text_generation(self) -> None:
        pending=self.prepare(); failed=self.prepare()
        self.call('record-run',failed,'--execution-status','failed')
        self.call('assess',failed,'--output-quality','no_output','--output-use','no_output')
        dest=self.root/'exported'
        result=self.call('export','--destination',str(dest))
        self.assertEqual(result['exported'],2); self.assertEqual(result['awaiting_run'],1)
        for rid in [pending,failed]:
            self.assertEqual(json.loads((dest/f'{rid}.json').read_text()),self.record(rid))
        self.assertEqual(self.call('export','--destination',str(dest))['files_changed'],0)
        self.assertFalse((dest/'.git').exists())

    def test_export_conflict_is_not_overwritten(self) -> None:
        rid=self.prepare(); dest=self.root/'exports'
        self.call('export','--destination',str(dest))
        path=dest/f'{rid}.json'; value=json.loads(path.read_text()); value['workspace_task']='Other source'
        path.write_text(json.dumps(value)); before=path.read_bytes()
        self.call('export','--destination',str(dest),error=True)
        self.assertEqual(path.read_bytes(),before)

    def test_export_subset_and_late_revision(self) -> None:
        rid=self.prepare(); other=self.prepare(); dest=self.root/'exports'
        self.call('export','--destination',str(dest),'--record-id',rid)
        self.assertFalse((dest/f'{other}.json').exists())
        self.start(rid); self.call('export','--destination',str(dest),'--record-id',rid)
        self.assertEqual(json.loads((dest/f'{rid}.json').read_text())['revision'],2)

    def test_missing_file_not_silently_empty(self) -> None:
        self.call('validate',error=True)
        self.call('export','--destination',str(self.root/'exports'),error=True)
        self.assertFalse((self.root/'exports').exists())

    def test_legacy_only_file_reports_coverage(self) -> None:
        self.file.parent.mkdir(); self.file.write_text('# Existing records\nHuman notes\n')
        result=self.call('validate')
        self.assertEqual(result['managed_records'],0)
        self.assertIn('legacy',result['note'])

    def test_real_cli_json_error_and_required_root(self) -> None:
        result=subprocess.run([sys.executable,str(SCRIPT),'prepare'],text=True,capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertFalse(json.loads(result.stderr)['ok'])

    def test_known_root_required_and_no_harness_discovery(self) -> None:
        with patch.object(d.Path,'resolve',wraps=self.root.resolve) as resolve:
            # Catalog, credentials, and host directories are never inspected.
            result=self.call('schema')
        self.assertIn('$schema',result)
        resolve.assert_not_called()

    def test_invalid_enum_cli_exits(self) -> None:
        proc=subprocess.run([sys.executable,str(SCRIPT),'--project-root',str(self.root),'assess','D0','--output-quality','good'],text=True,capture_output=True)
        self.assertEqual(proc.returncode,2); self.assertIn('invalid choice',proc.stderr)


    def test_pending_use_remains_visible(self) -> None:
        rid = self.prepare()
        self.start(rid)
        self.call('assess', rid, '--output-quality', 'unverified', '--output-use', 'pending')
        self.assertEqual(self.call('show')['records'][0]['pending_use_attempts'], 1)

    def test_export_symlink_does_not_replace_target(self) -> None:
        rid = self.prepare()
        destination = self.root / 'exports'
        destination.mkdir()
        target = self.root / 'private.txt'
        target.write_text('Keep')
        try:
            (destination / f'{rid}.json').symlink_to(target)
        except OSError:
            self.skipTest('Symlinks unavailable')
        self.call('export', '--destination', str(destination), error=True)
        self.assertEqual(target.read_text(), 'Keep')

    def test_long_note_does_not_change_record(self) -> None:
        rid = self.prepare()
        self.start(rid)
        original = self.file.read_bytes()
        self.call('assess', rid, '--output-quality', 'incomplete', '--output-use', 'pending',
                  '--note', 'x' * 201, error=True)
        self.assertEqual(self.file.read_bytes(), original)

    def test_shared_group_does_not_copy_parent_metrics(self) -> None:
        first = self.prepare(group_id='G1')
        second = self.prepare(group_id='G1')
        self.start(first)
        self.call('assess', first, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is',
                  '--parent-work-seconds', '5')
        self.assertEqual(self.record(second)['parent_metrics'], {})

    def test_schema_and_enum_reference_agree(self) -> None:
        text = (ROOT / 'references' / 'recording-tool.md').read_text()
        for definition in ['task_type', 'difficulty', 'selection_reason', 'quality', 'use', 'status',
                           'expected_benefit', 'delegation_usefulness']:
            for value in d.SCHEMA['$defs'][definition]['enum']:
                if value is not None:
                    self.assertIn('`' + value + '`', text)

    def test_conflicting_unknown_future_record_rejected(self) -> None:
        rid = self.prepare()
        record = self.record(rid)
        record['schema_version'] = 999
        with self.assertRaises(d.RecordError):
            d.validate_record(record)

    def test_mixed_line_endings_preserve_surrounding_text(self) -> None:
        rid = self.prepare()
        text = self.file.read_text()
        before, block = text.split(d.START, 1)
        mixed = before.replace('\n', '\r\n') + d.START + block
        self.file.write_bytes(mixed.encode())
        self.start(rid)
        self.call('validate')
        self.assertTrue(self.file.read_bytes().startswith(before.replace('\n', '\r\n').encode()))

    def test_marker_like_text_inside_unicode_json_string_is_data(self) -> None:
        description = 'Data\u2028<!-- adaptive-delegation:records:v99 -->'
        rid = self.prepare(task_description=description)
        self.start(rid)
        self.assertEqual(self.record(rid)['task']['description'], description)


    def test_expected_benefit_is_required_before_new_delegation(self) -> None:
        self.call('prepare', '--task-type', 'verify', '--task-description', 'Check',
                  '--requested-child-model', 'example/worker', error=True)
        self.assertFalse(self.file.exists())
        rid = self.prepare(expected_delegation_benefit='independent_check', model_selection_reason='default')
        rec = self.record(rid)
        self.assertEqual(rec['expected_delegation_benefit'], 'independent_check')
        self.assertEqual(rec['model_selection_reason'], 'default')
        self.assertEqual(rec['execution_mode'], 'delegate')
        original = self.file.read_bytes()
        self.call('record-run', rid, '--json', '-',
                  stdin='{"expected_delegation_benefit":"save_cost"}', error=True)
        self.assertEqual(self.file.read_bytes(), original)

    def test_correct_used_output_can_have_negative_delegation_value(self) -> None:
        rid = self.prepare(); aid = self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is',
                  '--delegation-usefulness', 'burden_exceeded_benefit')
        rec = self.record(rid)
        self.assertEqual(rec['attempts'][0]['assessment']['output_quality'], 'meets_requirements')
        self.assertEqual(rec['delegation_assessment']['delegation_usefulness'], 'burden_exceeded_benefit')
        self.assertEqual(rec['delegation_assessment']['attempt_ids'], [aid])
        self.assertNotIn('delegation_usefulness', rec['attempts'][0]['assessment'])
        self.assertFalse(self.call('show')['records'][0]['delegation_review_pending'])

    def test_unused_output_can_resolve_uncertainty(self) -> None:
        rid = self.prepare(expected_delegation_benefit='independent_check'); self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'not_used',
                  '--delegation-usefulness', 'helpful')
        self.assertEqual(self.record(rid)['delegation_assessment']['delegation_usefulness'], 'helpful')

    def test_usefulness_unknown_does_not_fabricate_metrics(self) -> None:
        rid = self.prepare(expected_delegation_benefit='save_cost'); self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is',
                  '--delegation-usefulness', 'unknown')
        rec = self.record(rid)
        self.assertNotIn('cost_amount', rec['attempts'][0]['metrics'])
        self.assertEqual(rec['parent_metrics'], {})
        self.assertFalse(self.call('show')['records'][0]['delegation_review_pending'])

    def test_missing_usefulness_is_not_inferred_from_quality(self) -> None:
        rid = self.prepare(); self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is')
        self.assertIsNone(self.record(rid).get('delegation_assessment'))
        self.assertTrue(self.call('show')['records'][0]['delegation_review_pending'])
        self.call('assess', rid, '--delegation-usefulness', 'no_benefit')
        self.assertFalse(self.call('show')['records'][0]['delegation_review_pending'])

    def test_whole_delegation_review_covers_retries_not_last_output(self) -> None:
        rid = self.prepare(); first = self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is',
                  '--delegation-usefulness', 'helpful')
        second = self.call('record-run', rid, '--new-attempt', '--retry-of', first, '--run-id', 'R2',
                           '--execution-status', 'completed')['attempt_id']
        self.assertTrue(self.call('show')['records'][0]['delegation_review_pending'])
        self.call('assess', rid, '--attempt-id', second, '--output-quality', 'incorrect',
                  '--output-use', 'used_after_major_rework', '--delegation-usefulness', 'burden_exceeded_benefit')
        rec = self.record(rid)
        self.assertEqual(rec['delegation_assessment']['attempt_ids'], [first, second])
        self.assertEqual(rec['delegation_assessment_history'][0]['previous']['delegation_usefulness'], 'helpful')
        self.assertFalse(self.call('show')['records'][0]['delegation_review_pending'])

    def test_usefulness_updates_are_idempotent_and_corrections_preserved(self) -> None:
        rid = self.prepare(); self.start(rid)
        self.call('assess', rid, '--delegation-usefulness', 'helpful')
        original = self.file.read_bytes()
        self.assertFalse(self.call('assess', rid, '--delegation-usefulness', 'helpful')['changed'])
        self.assertEqual(self.file.read_bytes(), original)
        self.call('assess', rid, '--delegation-usefulness', 'no_benefit', error=True)
        self.assertEqual(self.file.read_bytes(), original)
        self.call('assess', rid, '--delegation-usefulness', 'no_benefit',
                  '--correction-reason', 'Review duplicated work already done.')
        self.assertEqual(self.record(rid)['delegation_assessment_history'][0]['previous']['delegation_usefulness'], 'helpful')

    def test_output_correction_reopens_utility_review_without_erasing_history(self) -> None:
        rid = self.prepare(); self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is',
                  '--delegation-usefulness', 'helpful')
        self.call('assess', rid, '--output-quality', 'incorrect', '--output-use', 'used_as_is',
                  '--correction-reason', 'Later test exposed an error.')
        rec = self.record(rid)
        self.assertIsNone(rec['delegation_assessment'])
        self.assertEqual(rec['delegation_assessment_history'][0]['previous']['delegation_usefulness'], 'helpful')
        self.assertTrue(self.call('show')['records'][0]['delegation_review_pending'])

    def test_late_metrics_do_not_erase_utility_judgment(self) -> None:
        rid = self.prepare(); self.start(rid)
        self.call('assess', rid, '--output-quality', 'meets_requirements', '--output-use', 'used_as_is',
                  '--delegation-usefulness', 'helpful')
        review = copy.deepcopy(self.record(rid)['delegation_assessment'])
        self.call('record-run', rid, '--output-tokens', '12')
        self.assertEqual(self.record(rid)['delegation_assessment'], review)

    def test_usefulness_only_and_output_stage_input_boundaries(self) -> None:
        rid = self.prepare(); aid = self.start(rid); original = self.file.read_bytes()
        for fields in ({'output_quality':'incorrect'}, {'note':'unattached'},
                       {'delegation_usefulness':'good'}, {'delegation_usefulness':'helpful','output_use':'not_used'}):
            self.call('assess', rid, '--json', '-', stdin=json.dumps(fields), error=True)
            self.assertEqual(self.file.read_bytes(), original)
        self.call('assess', rid, '--attempt-id', aid, '--delegation-usefulness', 'helpful', error=True)
        self.call('assess', rid, '--delegation-usefulness', 'unknown')

    def test_nonterminal_utility_is_unknown_and_remains_pending(self) -> None:
        rid = self.prepare()
        self.call('record-run', rid, '--execution-status', 'running')
        self.call('assess', rid, '--delegation-usefulness', 'helpful', error=True)
        self.call('assess', rid, '--delegation-usefulness', 'unknown')
        self.assertTrue(self.call('show')['records'][0]['delegation_review_pending'])

    def test_direct_choice_has_no_child_and_no_pending_run(self) -> None:
        rid = self.call('record-direct', '--task-type', 'lookup', '--task-description', 'Read the already located option.',
                        '--direct-reason', 'Briefing and checking would duplicate a short read.')['record_id']
        rec = self.record(rid); summary = self.call('show')['records'][0]
        self.assertEqual(rec['execution_mode'], 'direct')
        self.assertEqual(rec['attempts'], [])
        for key in ('requested_child','model_selection_reason','expected_delegation_benefit','delegation_assessment'):
            self.assertNotIn(key, rec)
        self.assertEqual(summary['unassessed_attempts'], 0)
        self.assertFalse(summary['awaiting_run'])
        self.assertFalse(summary['delegation_review_pending'])
        original = self.file.read_bytes()
        self.call('record-run', rid, '--execution-status', 'completed', error=True)
        self.call('assess', rid, '--output-quality', 'no_output', '--output-use', 'no_output', error=True)
        self.assertEqual(self.file.read_bytes(), original)

    def test_direct_stage_rejects_child_fields_and_requires_short_reason(self) -> None:
        fields = {'task_type':'lookup','task_description':'Read one source.','direct_reason':'Already have the source.'}
        for extra in ({'requested_child_model':'x'}, {'direct_reason':None}, {'direct_reason':' '},
                      {'direct_reason':'x'*201}, {'expected_delegation_benefit':'save_time'}):
            self.call('record-direct', '--json', '-', stdin=json.dumps({**fields, **extra}), error=True)
            self.assertFalse(self.file.exists())
        fields.pop('direct_reason')
        self.call('record-direct', '--json', '-', stdin=json.dumps(fields), error=True)

    def test_direct_schema_does_not_disguise_a_launch_failure(self) -> None:
        rid = self.call('record-direct', '--task-type', 'lookup', '--task-description', 'Read source.',
                        '--direct-reason', 'No useful independent work.')['record_id']
        rec = self.record(rid)
        other = self.prepare(); self.start(other)
        for key, value in [('requested_child',{}), ('delegation_assessment',None),
                           ('attempts',self.record(other)['attempts'])]:
            altered = copy.deepcopy(rec); altered[key] = value
            with self.assertRaises(d.RecordError):
                d.validate_record(altered)

    def test_mixed_export_retains_direct_pending_failed_and_utility(self) -> None:
        pending = self.prepare(); failed = self.prepare()
        self.call('record-run', failed, '--execution-status', 'failed')
        self.call('assess', failed, '--output-quality', 'no_output', '--output-use', 'no_output',
                  '--delegation-usefulness', 'burden_exceeded_benefit')
        direct = self.call('record-direct', '--task-type', 'lookup', '--task-description', 'Read source.',
                           '--direct-reason', 'No useful independent work.')['record_id']
        dest = self.root/'exported'; result = self.call('export', '--destination', str(dest))
        self.assertEqual(result['exported'], 3)
        self.assertEqual(result['direct_records'], 1)
        self.assertEqual(result['awaiting_run'], 1)
        self.assertEqual(result['delegation_reviews_pending'], 1)
        for rid in (pending, failed, direct):
            self.assertEqual(json.loads((dest/f'{rid}.json').read_text()), self.record(rid))
        self.assertEqual(self.call('export', '--destination', str(dest))['files_changed'], 0)

    def test_older_records_do_not_gain_invented_benefits(self) -> None:
        rid = self.prepare(); self.start(rid)
        document = d.Document.parse(self.file.read_bytes()); rec = document.find(rid)
        rec.pop('execution_mode'); rec.pop('expected_delegation_benefit')
        self.file.write_bytes(document.render())
        self.call('record-run', rid, '--output-tokens', '4')
        self.assertNotIn('expected_delegation_benefit', self.record(rid))
        self.assertEqual(self.call('show')['records'][0]['execution_mode'], 'delegate')
        self.assertTrue(self.call('show')['records'][0]['delegation_review_pending'])

    def test_utility_cannot_reference_an_unobserved_attempt(self) -> None:
        rid = self.prepare(); self.start(rid)
        self.call('assess', rid, '--delegation-usefulness', 'unknown')
        rec = self.record(rid); rec['delegation_assessment']['attempt_ids'] = ['UnknownAttempt']
        with self.assertRaises(d.RecordError):
            d.validate_record(rec)

if __name__ == '__main__':
    unittest.main()
