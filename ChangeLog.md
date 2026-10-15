# Changelog

## 1.2.0 — first community release — 2026-10-15

The first release maintained in this community fork includes the changes below
since the inherited `1.1.2` tag. The benchmark remains Ubuntu 20.04 DISA STIG
V1R7; the role release number does not change the benchmark revision.

- Continue maintenance and contributions in [karlg100/UBUNTU20-STIG](https://github.com/karlg100/UBUNTU20-STIG), with support and review hosted in this repository.
- Correct audit-rule reporting so unchanged rules do not report changes ([PR #6](https://github.com/karlg100/UBUNTU20-STIG/pull/6)).
- Honor the UBTU-20-010072 disable flag ([PR #9](https://github.com/karlg100/UBUNTU20-STIG/pull/9)).
- Gate automatic reboots on persistent reboot requirements and preserve pending requests when reboot is skipped ([PR #10](https://github.com/karlg100/UBUNTU20-STIG/pull/10)).
- Refresh APT metadata only when its configurable cache age expires; the default is two hours ([PR #11](https://github.com/karlg100/UBUNTU20-STIG/pull/11)).
- Restrict excessive audit-log permissions while preserving already compliant modes ([PR #12](https://github.com/karlg100/UBUNTU20-STIG/pull/12)).
- Complete UBTU-20-010124 remediation for auditd's configured log group, log directory, and log files, with an independent daemon configuration reload ([PR #15](https://github.com/karlg100/UBUNTU20-STIG/pull/15)).
- Reconcile the role's three faillock PAM profiles as one family and support explicit migration to selected external profiles, with conflict checks and rollback on generation failure ([PR #17](https://github.com/karlg100/UBUNTU20-STIG/pull/17)).
- Replace inherited infrastructure-dependent CI with GitHub-hosted static checks and remove automatic Galaxy publishing.
- Add 20 regression tests exercising the actual faillock control with stock Ubuntu 20.04 PAM tooling in a disposable container.
- Update contributor, installation, configuration, and testing guidance for the independent community fork.

### Upgrade notes

- Pin role installations to the `1.2.0` Git tag. Install and validate runtime collections separately as described in [Distribution](README.md#distribution).
- A disabled faillock control remains a no-op by default. Existing deployments that need to remove legacy role profiles must explicitly configure `ubtu20stig_faillock_migrate_to_profiles`; read [the migration guidance](README.md#pam-faillock-ownership-and-legacy-migration) before enabling it.
- An expired APT cache can legitimately report a change. Skipped reboots remain pending until a reboot occurs.

### Validation scope

The earlier audit and idempotence fixes passed a real-host repeat run with
`ok=208 changed=0 unreachable=0 failed=0`. The subsequent faillock migration
change is covered by 20 native PAM configuration regression tests, including
repeat runs. Those tests do not establish login/lockout acceptance or full-role
convergence with the migration enabled. Validate the release and site-specific
settings on a representative Ubuntu 20.04 system before deployment.

## Inherited Ansible Lockdown history

The entries below describe the original project. References to its releases, issue numbers, and support channels are historical; current support is documented in [SUPPORT.md](SUPPORT.md).

### Based on Stig v1r7 - Jan 2023

- ansible version updated to 2.10.1 minimum
- updates to pre-commit config
- gitignore updated

### Release 0.9.1

- yamllint update
- ansible-lint updated
- linting
- workflow
- readme layout
- discord link
- precommit added

Issues

- thanks to @kfiresmith
  - [ansible-lockdown/UBUNTU20-STIG#11](https://github.com/ansible-lockdown/UBUNTU20-STIG/issues/11)
  - [ansible-lockdown/UBUNTU20-STIG#12](https://github.com/ansible-lockdown/UBUNTU20-STIG/issues/12)
- thanks to @alex-rowe
  - [ansible-lockdown/UBUNTU20-STIG#13](https://github.com/ansible-lockdown/UBUNTU20-STIG/issues/13)

### Release 0.9.0

### April 2023 Updates

- Ansible-lint Check
- Yamllint Updated File
- Yamllint Check
- Updated Module Names To Full
- Updated License
- Updated Readme To New Format

### Initial Release

- Updated to release V1R7
