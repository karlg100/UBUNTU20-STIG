#!/usr/bin/env python3
"""Native Focal PAM regression tests. Target only a labelled disposable container."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from jinja2 import Template

ROOT = Path(__file__).resolve().parents[2]
OWNED = {'faillockpre', 'faillockmain', 'faillockpost'}
EXTERNAL = ['fixture-preauth', 'fixture-authfail', 'fixture-authsucc']
CONTAINER = None


def docker(*args, data=None):
    return subprocess.check_output(['docker', 'exec', '-i', CONTAINER, *args], input=data, text=True)


def remote(code, value=None):
    return docker('python3', '-c', 'import json,sys,os,base64,shutil\nfrom pathlib import Path\n' + code,
                  data=json.dumps(value))


def read(path):
    return docker('cat', path)


def write(path, text):
    remote('p,s=json.load(sys.stdin); Path(p).write_text(s)', [path, text])


def selected():
    result = docker('env', 'DEBIAN_FRONTEND=noninteractive', 'debconf-communicate',
                    'libpam-runtime', data='GET libpam-runtime/profiles\n')
    assert result.startswith('0 '), result
    return set(result[2:].strip().split(', '))


def update(*args):
    return docker('env', 'DEBIAN_FRONTEND=noninteractive', '/usr/sbin/pam-auth-update', '--package', *args)


def snapshot():
    # Byte comparison of PAM inputs, outputs, caches and the generator; debconf
    # selection is checked separately (its UI/template metadata can change).
    result = remote('''
result={}
for directory in ['/usr/share/pam-configs','/etc/pam.d','/var/lib/pam']:
 for p in Path(directory).iterdir():
  if p.is_symlink(): result[str(p)]={'link':os.readlink(str(p))}
  elif p.is_file(): result[str(p)]={'data':base64.b64encode(p.read_bytes()).decode(), 'mode':p.stat().st_mode & 0o7777}
result['/usr/sbin/pam-auth-update']={'data':base64.b64encode(Path('/usr/sbin/pam-auth-update').read_bytes()).decode()}
print(json.dumps(result,sort_keys=True))
''')
    return json.loads(result), selected()


def auth_entries():
    result = []
    for line in read('/etc/pam.d/common-auth').splitlines():
        match = re.match(r'^auth\s+(\[[^\]]+\]|\S+)\s+\S*pam_faillock\.so\s+(.*)$', line)
        if match:
            control, options = match.groups()
            result.append((control, tuple(options.split())))
    return result


class NativePamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        info = json.loads(subprocess.check_output(['docker', 'inspect', CONTAINER], text=True))[0]
        assert info['Config']['Labels'].get('codex.task') == 'ubuntu20-pam-issue16'
        assert not info['Mounts'], 'Native tests must never have host mounts'
        assert 'VERSION_ID="20.04"' in read('/etc/os-release')
        if remote("print(Path('/tmp/stig-pam-baseline.tar').exists())").strip() == 'True':
            cls.reset()
        generator = read('/usr/sbin/pam-auth-update')
        assert "elsif ($opt eq '--remove')" in generator and "elsif ($opt eq '--disable')" not in generator
        cls.generator_sha = hashlib.sha256(generator.encode()).hexdigest()
        package_md5 = next(line.split()[0] for line in read('/var/lib/dpkg/info/libpam-runtime.md5sums').splitlines()
                           if line.split()[-1] == 'usr/sbin/pam-auth-update')
        assert hashlib.md5(generator.encode()).hexdigest() == package_md5, 'Use the stock packaged generator'
        print('Native PAM packages:', docker('dpkg-query', '-W', 'libpam-runtime', 'libpam-modules').strip())
        print('pam-auth-update SHA256:', cls.generator_sha)
        print(subprocess.check_output(['ansible-playbook', '--version'], text=True).splitlines()[0])
        # Save the pristine disposable environment, including its private test debconf DB.
        docker('tar', '-cf', '/tmp/stig-pam-baseline.tar', '-C', '/', 'etc/pam.d',
               'usr/share/pam-configs', 'var/lib/pam', 'var/cache/debconf', 'usr/sbin/pam-auth-update')
        cls.temp = tempfile.TemporaryDirectory(prefix='stig-pam-tests-')
        cls.play = Path(cls.temp.name) / 'play.yml'
        cls.play.write_text(json.dumps([{'hosts': 'all', 'gather_facts': False, 'tasks': [
            {'name': 'Exercise the actual tagged control', 'ansible.builtin.import_role': {
                'name': str(ROOT), 'tasks_from': 'fix-cat3'}}]}]))
        cls.role_profiles = {name: Template((ROOT / 'templates/pam-configs' /
                                            ('pam-configs-profile-%s.j2' % name)).read_text()).render().lstrip('\n') + '\n'
                             for name in OWNED}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.reset()
        self.assertEqual(hashlib.sha256(read('/usr/sbin/pam-auth-update').encode()).hexdigest(), self.generator_sha)

    @staticmethod
    def reset():
        remote('''
for directory in ['/usr/share/pam-configs','/etc/pam.d','/var/lib/pam','/var/cache/debconf']:
 shutil.rmtree(directory)
''')
        docker('tar', '-xf', '/tmp/stig-pam-baseline.tar', '-C', '/')

    def apply(self, enabled=True, targets=None, changed=0, failure=None, check=False, tags='UBTU-20-010072'):
        variables = {'ubtu_20_010072': enabled, 'ubtu20stig_faillock_migrate_to_profiles': targets or [],
                     'ansible_connection': 'community.docker.docker', 'ansible_python_interpreter': '/usr/bin/python3'}
        command = ['ansible-playbook', '-i', CONTAINER + ',', str(self.play),
                   '--tags', tags, '-e', json.dumps(variables)]
        if check:
            command.append('--check')
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if failure:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(failure, result.stdout)
        else:
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertRegex(result.stdout, r'changed=%s\s+unreachable=0\s+failed=0' % changed)
        return result.stdout

    def install_owned(self, enable=OWNED):
        for name, content in self.role_profiles.items():
            write('/usr/share/pam-configs/' + name, content)
        update('--enable', *sorted(enable))

    def install_external(self, control='requisite', spaces='  ', options='audit', enable=True):
        profiles = {
            EXTERNAL[0]: 'Name: Test preauth\nDefault: no\nPriority: 1000\nAuth-Type: Primary\nAuth:\n    %s%spam_faillock.so%spreauth %s\n' % (control, spaces, spaces, options),
            EXTERNAL[1]: 'Name: Test authfail\nDefault: no\nPriority: 0\nAuth-Type: Primary\nAuth:\n    [default=die] pam_faillock.so authfail audit\nAccount-Type: Primary\nAccount:\n    required pam_faillock.so\n',
            EXTERNAL[2]: 'Name: Test authsucc\nDefault: no\nPriority: 0\nAuth-Type: Additional\nAuth:\n    sufficient%spam_faillock.so authsucc audit\n' % spaces,
        }
        for name, content in profiles.items():
            write('/usr/share/pam-configs/' + name, content)
        if enable:
            update('--enable', *EXTERNAL)

    def install_unrelated(self):
        write('/usr/share/pam-configs/fixture-unrelated',
              'Name: Unrelated test profile\nDefault: no\nPriority: 1\nAuth-Type: Additional\nAuth:\n    optional pam_permit.so\n')
        update('--enable', 'fixture-unrelated')

    def coexist(self, **kwargs):
        self.install_external(**kwargs)
        self.install_owned({'faillockpre', 'faillockpost'})
        self.assertEqual(len(auth_entries()), 5)
        self.assertNotIn('faillockmain', selected())

    def assert_retired(self):
        self.assertFalse(selected() & OWNED)
        for name in OWNED:
            self.assertEqual(docker('test', '!', '-e', '/usr/share/pam-configs/' + name), '')
        entries = auth_entries()
        self.assertEqual(len(entries), 3)
        actions = collections.Counter(action for _, options in entries for action in options
                                      if action in {'preauth', 'authfail', 'authsucc'})
        self.assertEqual(actions, {'preauth': 1, 'authfail': 1, 'authsucc': 1})

    def test_clean_enabled_and_regenerated_repeat(self):
        self.install_unrelated()
        unrelated = read('/usr/share/pam-configs/fixture-unrelated')
        original_selection = selected()
        self.apply(changed=1)
        self.assertEqual(selected(), original_selection | OWNED)
        self.assertEqual(auth_entries(), [('required', ('preauth',)), ('[default=die]', ('authfail',)),
                                         ('sufficient', ('authsucc',))])
        stable = snapshot()
        self.apply()
        self.assertEqual(snapshot(), stable)
        update()
        self.assertEqual(snapshot(), stable)
        self.apply()
        self.assertEqual(read('/usr/share/pam-configs/fixture-unrelated'), unrelated)

    def test_partial_role_owned_family_is_completed(self):
        self.install_owned({'faillockpre', 'faillockpost'})
        self.apply(changed=1)
        self.assertEqual(len(auth_entries()), 3)
        self.apply()

    def test_disabled_clean_noop(self):
        before = snapshot()
        self.apply(enabled=False)
        self.assertEqual(snapshot(), before)

    def test_disabled_legacy_noop(self):
        self.coexist()
        before = snapshot()
        self.apply(enabled=False)
        self.assertEqual(snapshot(), before)

    def test_coexistence_migration_and_regenerated_repeat(self):
        self.install_unrelated()
        self.coexist()
        retained_files = {name: read('/usr/share/pam-configs/' + name) for name in EXTERNAL + ['fixture-unrelated']}
        before = selected()
        self.apply(enabled=False, targets=EXTERNAL, changed=1)
        self.assert_retired()
        self.assertEqual(selected(), before - OWNED)
        self.assertEqual(auth_entries(), [('requisite', ('preauth', 'audit')), ('[default=die]', ('authfail', 'audit')),
                                         ('sufficient', ('authsucc', 'audit'))])
        stable = snapshot()
        self.apply(enabled=False, targets=EXTERNAL)
        self.assertEqual(snapshot(), stable)
        update()
        self.assertEqual(snapshot(), stable)
        self.apply(enabled=False, targets=EXTERNAL)
        for name, content in retained_files.items():
            self.assertEqual(read('/usr/share/pam-configs/' + name), content)

    def test_explicit_external_controls_spacing_and_options(self):
        for control, spaces, options in [('required', '\t', 'audit silent'), ('requisite', '   ', 'audit deny=3')]:
            with self.subTest(control=control):
                self.setUp()
                self.coexist(control=control, spaces=spaces, options=options)
                self.apply(enabled=False, targets=EXTERNAL, changed=1)
                self.assert_retired()
                self.assertEqual(auth_entries()[0], (control, tuple(('preauth ' + options).split())))
                stable = snapshot()
                update()
                self.apply(enabled=False, targets=EXTERNAL)
                self.assertEqual(snapshot(), stable)

    def test_enabled_conflicting_owner_refused_without_writes(self):
        self.install_external()
        before = snapshot()
        self.apply(failure='Competing selected faillock profiles')
        self.assertEqual(snapshot(), before)

    def test_enabled_and_migration_are_mutually_exclusive(self):
        self.coexist()
        before = snapshot()
        self.apply(targets=EXTERNAL, failure='Choose enabled role ownership')
        self.assertEqual(snapshot(), before)

    def test_incomplete_or_unselected_target_refused(self):
        self.install_owned()
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='already selected external')
        self.assertEqual(snapshot(), before)
        self.install_external(enable=False)
        update('--enable', EXTERNAL[0])
        before = snapshot()
        self.apply(enabled=False, targets=[EXTERNAL[0]], failure='exactly one preauth, authfail and authsucc')
        self.assertEqual(snapshot(), before)

    def test_distinct_control_flags_are_not_assumed_equivalent(self):
        self.coexist(control='optional')
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='Unsupported preauth PAM control flag')
        self.assertEqual(snapshot(), before)

    def test_customized_legacy_profile_refused(self):
        self.coexist()
        path = '/usr/share/pam-configs/faillockpre'
        write(path, read(path).replace('required', 'requisite'))
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='has been customized')
        self.assertEqual(snapshot(), before)

    def test_legacy_symlink_refused(self):
        self.coexist()
        docker('mv', '/usr/share/pam-configs/faillockpre', '/tmp/legacy-preauth')
        docker('ln', '-s', '/tmp/legacy-preauth', '/usr/share/pam-configs/faillockpre')
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='non-symlink PAM file')
        self.assertEqual(snapshot(), before)

    def test_misordered_retained_family_refused(self):
        self.coexist()
        path = '/usr/share/pam-configs/' + EXTERNAL[0]
        write(path, read(path).replace('Priority: 1000', 'Priority: 100'))
        update()
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='preauth must precede')
        self.assertEqual(snapshot(), before)

    def test_unattributed_common_auth_line_refused(self):
        self.install_external()
        path = '/etc/pam.d/common-auth'
        write(path, read(path) + 'auth required pam_faillock.so preauth\n')
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='differ from pam-auth-update provenance')
        self.assertEqual(snapshot(), before)

    def test_refused_native_regeneration_restores_inputs(self):
        path = '/etc/pam.d/common-auth'
        write(path, read(path).replace('auth\t[success=', 'auth optional pam_permit.so\nauth\t[success='))
        before = snapshot()
        self.apply(failure='declined or failed regeneration')
        self.assertEqual(snapshot(), before)

    def test_failed_command_rolls_back_generated_stack_and_selections(self):
        # Explicit fault injection, separate from stock-tool behavior tests.
        self.coexist()
        docker('cp', '/usr/sbin/pam-auth-update', '/tmp/pam-auth-update-real')
        write('/usr/sbin/pam-auth-update', '#!/bin/sh\n/tmp/pam-auth-update-real "$@"\nexit 9\n')
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, failure='declined or failed regeneration')
        self.assertEqual(snapshot(), before)

    def test_generator_exec_failure_restores_inputs(self):
        docker('chmod', '0644', '/usr/sbin/pam-auth-update')
        before = snapshot()
        self.apply(failure='Permission denied')
        self.assertEqual(snapshot(), before)

    def test_unseen_default_profile_cannot_be_auto_selected(self):
        self.install_external(enable=False)
        path = '/usr/share/pam-configs/' + EXTERNAL[0]
        write(path, read(path).replace('Default: no', 'Default: yes'))
        before = snapshot()
        self.apply(failure='Unseen default PAM profiles')
        self.assertEqual(snapshot(), before)

    def test_profile_conflicts_cannot_remove_unrelated_selection(self):
        self.install_unrelated()
        path = '/usr/share/pam-configs/fixture-unrelated'
        write(path, read(path) + 'Conflicts: faillockpre\n')
        before = snapshot()
        self.apply(failure='Conflicts declarations')
        self.assertEqual(snapshot(), before)

    def test_check_mode_predicts_without_writes(self):
        before = snapshot()
        self.apply(changed=1, check=True)
        self.assertEqual(snapshot(), before)
        self.coexist()
        before = snapshot()
        self.apply(enabled=False, targets=EXTERNAL, changed=1, check=True)
        self.assertEqual(snapshot(), before)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--container', required=True)
    options, remaining = parser.parse_known_args()
    CONTAINER = options.container
    unittest.main(argv=[__file__] + remaining, verbosity=2)
