#!/usr/bin/python
# Copyright (c) 2026 Ubuntu 20.04 STIG community contributors
# SPDX-License-Identifier: MIT
"""Reconcile one faillock owner using stock Focal pam-auth-update."""

DOCUMENTATION = r'''
---
module: ubtu20_pam_faillock
short_description: Reconcile the role's PAM faillock profiles
description:
  - Internal role module. Validates profile provenance before changing PAM.
  - Does not force regeneration or delete generated authentication lines.
options:
  manage:
    type: bool
    required: true
    description: Select the role-owned profile family.
  migrate_to:
    type: list
    elements: str
    default: []
    description: Explicitly retained, already selected external faillock profiles.
  role_profiles:
    type: dict
    required: true
    description: The three rendered role profiles, also used to establish ownership.
author:
  - Ubuntu 20.04 STIG community contributors
'''
EXAMPLES = r'''
# Normally invoked by tasks/pam_faillock.yml with rendered role profiles.
'''
RETURN = r'''
selected_profiles:
  description: Verified final profile selections.
  returned: success
  type: list
  elements: str
'''

import collections
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule

OWNED = {'faillockpre', 'faillockmain', 'faillockpost'}
KINDS = ('auth', 'account', 'password', 'session', 'session-noninteractive')
PROFILE_DIR = Path('/usr/share/pam-configs')
CACHE_DIR = Path('/var/lib/pam')
PAM_DIR = Path('/etc/pam.d')
PROFILE_KEY = 'libpam-runtime/profiles'
OVERRIDE_KEY = 'libpam-runtime/override'


class RollbackError(ValueError):
    """The caller must know that a failed update was not fully restored."""


def run_program(args, data=None):
    # Unlike AnsibleModule.run_command's startup-error path, an exec failure
    # raises here so that apply() can restore its snapshot before reporting it.
    return subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, env=dict(os.environ, DEBIAN_FRONTEND='noninteractive'), check=False)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_file(path):
    require(path.is_file() and not path.is_symlink(),
            'Expected a regular, non-symlink PAM file: %s' % path)
    return path.read_text()


def parse_profile(content):
    """Read the RFC822-like profile format; normalize whitespace, not controls."""
    fields = {}
    field = None
    for line in content.splitlines():
        if not line.strip():
            continue
        match = re.match(r'^(\S+):\s*(.*)$', line)
        if match:
            field, value = match.groups()
            field = re.sub(r'-Final$', '', field)
            require(field not in fields, 'Duplicate PAM profile field: %s' % field)
            fields[field] = [value.strip()] if value.strip() else []
        else:
            require(field is not None and line[:1].isspace(),
                    'Unsupported PAM profile syntax; review the profile before migration')
            fields[field].append(line.strip())
    return {key: tuple(' '.join(line.split()) for line in value)
            for key, value in fields.items()}


def pam_entry(line):
    line = line.split('#', 1)[0].strip()
    match = re.match(r'^(\[[^\]]+\]|\S+)\s+(\S+)(?:\s+(.*))?$', line)
    require(match is not None, 'Unsupported PAM entry; review the profile before migration')
    control, module, arguments = match.groups()
    return (' '.join(control.split()), os.path.basename(module),
            tuple((arguments or '').split()))


def faillock_entries(lines):
    entries = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        entry = pam_entry(line)
        if entry[1] == 'pam_faillock.so':
            entries.append(entry)
    return entries


def has_faillock(profile):
    return any('pam_faillock.so' in line for field, lines in profile.items()
               if field in ('Auth', 'Auth-Initial', 'Account', 'Account-Initial',
                            'Password', 'Session', 'Session-noninteractive')
               for line in lines)


def read_cache(kind):
    result = []
    name = None
    for line in read_file(CACHE_DIR / kind).splitlines():
        if line.startswith('Module: '):
            name = line[8:]
        elif line.strip():
            require(name is not None, 'PAM provenance cache is malformed')
            result.append((name, line))
    return result


def common_entries(kind):
    pam_type = kind.split('-')[0]
    lines = []
    for line in read_file(PAM_DIR / ('common-' + kind)).splitlines():
        stripped = line.split('#', 1)[0].strip()
        if not stripped:
            continue
        pieces = stripped.split(None, 1)
        require(len(pieces) == 2 and pieces[0] == pam_type,
                'Unsupported PAM syntax in common-%s; review local edits' % kind)
        lines.append(pieces[1])
    return faillock_entries(lines)


def check_stack(profiles, selected):
    """Require saved provenance and real faillock entries to agree exactly."""
    cached_profiles = set()
    for kind in KINDS:
        cache = read_cache(kind)
        cached_profiles.update(name for name, _ in cache if name != 'null')
        expected = collections.Counter(faillock_entries(line for _, line in cache))
        actual = collections.Counter(common_entries(kind))
        require(actual == expected,
                'Faillock entries in common-%s differ from pam-auth-update provenance; '
                'reconcile local edits before running this control' % kind)
        for name in selected:
            if name not in profiles:
                continue
            field = kind.capitalize()
            if kind == 'session-noninteractive' and 'Session-Interactive-Only' not in profiles[name]:
                field = 'Session'
            definition = profiles[name].get(field, ())
            recorded = [line for owner, line in cache if owner == name]
            require(collections.Counter(faillock_entries(definition)) ==
                    collections.Counter(faillock_entries(recorded)),
                    'Faillock profile %s differs from the generated cache; '
                    'regenerate and review the external owner first' % name)
    require(cached_profiles == selected,
            'Debconf selections and PAM provenance disagree; reconcile them before migration')


def validate_family(profiles, names):
    """Accept only an explicitly owned three-action family, preserving its flags."""
    actions = {}
    for name in names:
        profile = profiles[name]
        require('Auth-Initial' not in profile, 'Faillock Auth-Initial variants require manual review')
        require(has_faillock(profile), 'Retained profile %s is not a faillock profile' % name)
        for entry in faillock_entries(profile.get('Auth', ())):
            modes = set(entry[2]) & {'preauth', 'authfail', 'authsucc'}
            require(len(modes) == 1, 'Each faillock auth entry must have exactly one action')
            action = modes.pop()
            require(action not in actions, 'Duplicate retained faillock action: %s' % action)
            expected_controls = {'preauth': {'required', 'requisite'},
                                 'authfail': {'[default=die]'}, 'authsucc': {'sufficient'}}
            require(entry[0] in expected_controls[action],
                    'Unsupported %s PAM control flag: %s; review the external policy' % (action, entry[0]))
            expected_type = 'Additional' if action == 'authsucc' else 'Primary'
            require(profile.get('Auth-Type') == (expected_type,),
                    '%s must be in the %s PAM block' % (action, expected_type))
            require(profile.get('Priority') and len(profile['Priority']) == 1,
                    'Missing profile priority')
            actions[action] = (int(profile['Priority'][0]), name)
    require(set(actions) == {'preauth', 'authfail', 'authsucc'},
            'Retained profiles must already provide exactly one preauth, authfail and authsucc action')
    require(actions['preauth'] > actions['authfail'],
            'The retained preauth profile must precede authfail')


def validate_primary_order(profiles, selected):
    primary = []
    for name in sorted(selected, key=lambda item: (int(profiles[item]['Priority'][0]), item), reverse=True):
        profile = profiles[name]
        if profile.get('Auth-Type') == ('Primary',):
            primary.extend(pam_entry(line) for line in profile.get('Auth', ()))
    require(primary and primary[0][1] == 'pam_faillock.so' and 'preauth' in primary[0][2],
            'Faillock preauth must precede the other Primary authentication entries; review profile priorities')
    require(primary[-1][1] == 'pam_faillock.so' and 'authfail' in primary[-1][2],
            'Faillock authfail must follow the other Primary authentication entries; review profile priorities')


class Reconciler:
    def __init__(self, module):
        self.module = module

    def debconf(self, command):
        result = run_program(
            ['/usr/bin/debconf-communicate', 'libpam-runtime'],
            data=command + '\n')
        require(result.returncode == 0 and result.stdout.startswith('0 '), 'Cannot read or update PAM debconf state')
        return result.stdout[2:].strip()

    def selected(self):
        return set(filter(None, (name.strip() for name in self.debconf('GET ' + PROFILE_KEY).split(','))))

    def run(self):
        manage = self.module.params['manage']
        targets = self.module.params['migrate_to']
        require(manage != bool(targets),
                'Choose enabled role ownership OR disable ubtu_20_010072 and explicitly set '
                'ubtu20stig_faillock_migrate_to_profiles')
        require(len(targets) == len(set(targets)) and all(
            re.fullmatch(r'[A-Za-z0-9_-]+', name) and name not in OWNED for name in targets),
            'Migration targets must be distinct external profile names')
        desired = self.module.params['role_profiles']
        require(set(desired) == OWNED, 'Expected all three rendered STIG profiles')
        expected = {name: parse_profile(content) for name, content in desired.items()}
        profiles = {}
        for path in PROFILE_DIR.iterdir():
            if path.name.endswith('~') or re.fullmatch(r'#.+#', path.name):
                continue
            profiles[path.name] = parse_profile(read_file(path))
        for name in OWNED & profiles.keys():
            require(profiles[name] == expected[name],
                    'Legacy profile %s has been customized; refusing to overwrite or remove it' % name)
        selected = self.selected()
        require(selected and selected <= profiles.keys(), 'Selected PAM profiles are missing; repair them first')
        check_stack(profiles, selected)
        seen = set(read_file(CACHE_DIR / 'seen').splitlines())
        pending = {name for name, profile in profiles.items()
                   if profile.get('Default') == ('yes',) and name not in seen and name not in selected}
        require(not pending,
                'Unseen default PAM profiles would be selected automatically; '
                'settle them with their owner first: %s' % ', '.join(sorted(pending)))
        external = {name for name in selected - OWNED if has_faillock(profiles[name])}
        if manage:
            require(not external,
                    'Competing selected faillock profiles: %s. Disable ubtu_20_010072 and '
                    'explicitly migrate to a verified external family, or retire that family '
                    'with its owner before enabling STIG ownership' % ', '.join(sorted(external)))
            final = selected | OWNED
            validate_family(expected, OWNED)
            changed = not OWNED <= selected or any(
                name not in profiles or read_file(PROFILE_DIR / name) != desired[name] or
                stat.S_IMODE((PROFILE_DIR / name).stat().st_mode) != 0o644 or
                (PROFILE_DIR / name).stat().st_uid != 0 or (PROFILE_DIR / name).stat().st_gid != 0
                for name in OWNED)
        else:
            require(set(targets) == external,
                    'Migration must name exactly the already selected external faillock profiles; '
                    'install and verify the complete retained family first')
            validate_family(profiles, targets)
            final = selected - OWNED
            changed = bool(OWNED & (selected | profiles.keys()))
        # Conflicts must not silently deselect an unrelated profile or the retained owner.
        combined = dict(profiles, **expected) if manage else profiles
        validate_primary_order(combined, final)
        for name in final:
            conflicts = set(re.split(r',\s*', ' '.join(combined[name].get('Conflicts', ()))))
            require(not conflicts & final, 'PAM profile Conflicts declarations would deselect a retained profile')
        require(self.debconf('GET ' + OVERRIDE_KEY) == 'false',
                'PAM debconf override is set; clear it after reviewing local PAM modifications')
        if not changed or self.module.check_mode:
            self.module.exit_json(changed=changed, selected_profiles=sorted(final))
        self.apply(desired, manage, final)
        self.module.exit_json(changed=True, selected_profiles=sorted(final))

    def apply(self, desired, manage, final):
        paths = [PROFILE_DIR / name for name in OWNED] + [CACHE_DIR / 'seen']
        for kind in KINDS:
            paths.extend([PAM_DIR / ('common-' + kind + suffix) for suffix in ('', '.pam-new', '.pam-old')])
            paths.extend([CACHE_DIR / (kind + suffix) for suffix in ('', '.new')])
        snapshot = {}
        for path in paths:
            if path.exists() or path.is_symlink():
                read_file(path)  # Refuse symlinks before any write.
                snapshot[path] = (path.read_bytes(), path.stat())
            else:
                snapshot[path] = None
        debconf = {key: (self.debconf('GET ' + key), self.debconf('FGET %s seen' % key))
                   for key in (PROFILE_KEY, OVERRIDE_KEY)}
        try:
            if manage:
                for name, content in desired.items():
                    atomic_write(PROFILE_DIR / name, content.encode(), 0o644, 0, 0)
            args = ['/usr/sbin/pam-auth-update', '--package', '--enable' if manage else '--remove']
            result = run_program(args + sorted(OWNED))
            require(result.returncode == 0 and 'not updating' not in result.stderr,
                    'pam-auth-update declined or failed regeneration; review local PAM modifications')
            require(self.selected() == final,
                    'pam-auth-update changed unexpected selections; review conflicting profiles')
            profiles = {name: parse_profile(read_file(PROFILE_DIR / name)) for name in final}
            check_stack(profiles, final)
            if not manage:
                for name in OWNED:
                    path = PROFILE_DIR / name
                    if path.exists():
                        path.unlink()
        except Exception:
            try:
                for path, saved in snapshot.items():
                    if saved is None:
                        if path.exists():
                            path.unlink()
                    else:
                        data, info = saved
                        atomic_write(path, data, stat.S_IMODE(info.st_mode), info.st_uid, info.st_gid)
                        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
                for key, (value, seen) in debconf.items():
                    self.debconf('SET %s %s' % (key, value))
                    self.debconf('FSET %s seen %s' % (key, seen))
            except Exception as error:
                raise RollbackError('PAM update failed and rollback is incomplete; '
                                    'review the PAM configuration immediately: %s' % error) from error
            raise


def atomic_write(path, data, mode, uid, gid):
    # Stock pam-auth-update ignores #...# files, including one in flight.
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), prefix='#stig-pam-', suffix='#')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fchown(stream.fileno(), uid, gid)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    module = AnsibleModule(argument_spec={
        'manage': {'type': 'bool', 'required': True},
        'migrate_to': {'type': 'list', 'elements': 'str', 'default': []},
        'role_profiles': {'type': 'dict', 'required': True},
    }, supports_check_mode=True)
    try:
        Reconciler(module).run()
    except (OSError, ValueError) as error:
        module.fail_json(msg=str(error), changed=isinstance(error, RollbackError))


if __name__ == '__main__':
    main()
