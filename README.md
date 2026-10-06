# Ubuntu 20.04 DISA STIG — Community Fork

This repository is a community-maintained fork of [ansible-lockdown/UBUNTU20-STIG](https://github.com/ansible-lockdown/UBUNTU20-STIG). MindPoint Group no longer maintains the Ubuntu 20.04 role. Maintenance and contributions continue independently in [karlg100/UBUNTU20-STIG](https://github.com/karlg100/UBUNTU20-STIG).

The original work by MindPoint Group / Ansible Lockdown and its contributors remains credited. The [MIT license and original copyright notice](LICENSE) are preserved.

## Remediate Ubuntu 20.04 against the [DISA STIG](https://public.cyber.mil/stigs/downloads/)

### Based on [ Ubuntu 20.04 DISA STIG Version 1, Rel 7 released on Jan 26, 2023 ](https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CAN_Ubuntu_20-04_LTS_V1R7_STIG.zip)

---

[![Stars](https://img.shields.io/github/stars/karlg100/UBUNTU20-STIG?label=Repo%20Stars&style=social)](https://github.com/karlg100/UBUNTU20-STIG)
[![Issues Open](https://img.shields.io/github/issues-raw/karlg100/UBUNTU20-STIG?label=Open%20Issues)](https://github.com/karlg100/UBUNTU20-STIG/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/karlg100/UBUNTU20-STIG?label=Pull%20Requests)](https://github.com/karlg100/UBUNTU20-STIG/pulls)
[![License](https://img.shields.io/github/license/karlg100/UBUNTU20-STIG?label=License)](LICENSE)

---

## Community support

Use [this repository's issues](https://github.com/karlg100/UBUNTU20-STIG/issues) for questions, bug reports, and feature requests. Submit proposed changes as [pull requests](https://github.com/karlg100/UBUNTU20-STIG/pulls) targeting this repository's `devel` branch. See [SUPPORT.md](SUPPORT.md) for reporting and contribution guidance.

---

## Caution(s)

This role **will make changes to the system** which may have unintended consequences. This is not an auditing tool but rather a remediation tool to be used after an audit has been conducted.

Full-role check mode is not supported and is not a substitute for testing remediation on an Ubuntu 20.04 test system.

This role was developed against a clean install of the Ubuntu 20 operating system. If you are implementing to an existing system please review this role for any site specific changes that are needed.

### Reboot handling

`ubtu20_skip_reboot` defaults to `true`. After handlers finish, a normal role run checks Ubuntu's `/var/run/reboot-required` marker and the role's `/run/ubtu20stig-reboot-required` marker. It reboots only when a marker is present and automatic reboot is allowed. A skipped reboot produces an informational message without reporting a configuration change. Containers, chroots, and check mode never trigger an automatic reboot.

The role records successful GRUB updates and deferred changes to an immutable running audit configuration in its own marker. The marker remains pending across repeat runs until reboot clears `/run`; the role does not remove Ubuntu's marker. Immutable audit rules are assembled on disk for the next boot, without attempting a live load or restart. An unchanged audit configuration does not create a reboot request. Tagged runs that omit post-processing can leave a pending marker for a later full run.

Community fixes land in this fork's [devel branch](https://github.com/karlg100/UBUNTU20-STIG/tree/devel). See [releases](https://github.com/karlg100/UBUNTU20-STIG/releases) for published versions. Use a reviewed commit from this repository when pinning a deployment.

---

## Selecting STIG categories

The category switches `ubtu20stig_cat1_patch`, `ubtu20stig_cat2_patch`, and `ubtu20stig_cat3_patch` enable CAT I, CAT II, and CAT III tasks. All three default to `true`. Use these switches to select categories while retaining the role's supporting tasks. Individual control switches and task conditions also apply; review [defaults/main.yml](defaults/main.yml) for the complete configuration.

The category imports also provide the case-sensitive tags `cat1`, `cat2`, and `cat3`. Individual tasks may carry uppercase category tags, but those are not consistent selectors for an entire category. Selecting tags can omit prerequisite tasks, so validate the selected task sequence before applying it.

## Updating an existing deployment

Review the [changelog](ChangeLog.md), changed tasks, and variable defaults before adopting another revision. Validate the chosen role and dependency versions on a representative test system, including a repeat run with the same inputs.

## Auditing

This role performs remediation and includes manual-review warnings. It does not include an OpenSCAP report workflow or a standalone compliance scanner. Validate compliance separately against the benchmark used by your organization.

## Documentation

- [Community support and reporting problems](SUPPORT.md)
- [Requirements](#requirements)
- [Role variables and customization](#role-variables), with available settings in [defaults/main.yml](defaults/main.yml)
- [Control selection with tags](#tags)
- [Contributing changes](CONTRIBUTING.rst)
- [Issues](https://github.com/karlg100/UBUNTU20-STIG/issues) and [pull requests](https://github.com/karlg100/UBUNTU20-STIG/pulls)
- [Change history](ChangeLog.md)

## Requirements

- An Ubuntu 20.04 target. The role asserts the Ubuntu distribution and major version; it has no `skip_os_check` override.
- An Ansible controller, an inventory, connectivity to the target, and privilege escalation for remediation. See the official [installation guide](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html) and [getting-started guide](https://docs.ansible.com/projects/ansible/latest/getting_started/index.html).
- Python versions supported by your chosen Ansible and collection versions on the controller and target. The inherited role minimum in [metadata](meta/main.yml) and [the version assertion](vars/main.yml) is 2.10.1; this is not a tested compatibility matrix for every later release.
- The `community.general`, `community.crypto`, and `ansible.posix` collections declared in [meta/main.yml](meta/main.yml). See [Distribution](#distribution) for installation and [Testing](#testing) for the separate static-check environment.

Review the tasks and site-specific settings before applying the role. Authentication, networking, packages, and reboot behavior can affect access to an existing system.

## Role Variables

Use [defaults/main.yml](defaults/main.yml) as the configuration reference. Override values in inventory, `group_vars`, `host_vars`, or play variables so deployment settings stay separate from role source changes. Review individual control switches as well as the category switches; enabling a category does not make every control automatic. `ubtu20stig_disruption_high` defaults to `false` and enables tasks gated by that setting when changed to `true`.

### APT cache freshness

`ubtu20stig_apt_cache_valid_time` is the maximum age of cached APT metadata in seconds. It defaults to `7200` (two hours), matching the freshness interval used by the Ubuntu 22.04 and 24.04 roles. Set a non-negative integer; `0` requests a refresh on every run. The role preserves the APT module's change and failure reporting, so an expired cache can legitimately report a change and repository/signature errors still fail.

## Tags

Control tasks carry tags for STIG identifiers, severity, and the affected system component. Tags are case-sensitive and do not override task conditions. Use `ansible-playbook --list-tasks --tags <tag> -i <inventory> site.yml` to inspect the selected tasks before execution.

Below is an example of the tag section from a control within this role. Using this example if you set your run to skip all controls with the tag CCI-002824, this task will be skipped. The opposite can also happen where you run only controls tagged with CCI-002824.

```yaml
tags:
      - UBTU-20-010448
      - CAT2
      - CCI-002824
      - SRG-OS-000433-GPOS-00193
      - SV-238369r853446_rule
      - V-238369
      - kernel
```

## Community Contribution

Contributions to this community fork are welcome. See [CONTRIBUTING.rst](CONTRIBUTING.rst) for the workflow and Developer's Certificate of Origin.

- Work in a separate branch and submit pull requests to `karlg100/UBUNTU20-STIG:devel`.
- GPG-sign and sign off commits intended for merge.
- Link the relevant fork issue and describe the problem, fix, and validation performed.
- Record the checks that passed and any test-system validation still pending. For behavior changes, include an appropriate functional test and repeat-run results when available.

## Testing

[Community CI](.github/workflows/ci.yml) runs on pull requests and pushes to `devel` and `main`, and can be started manually. It runs YAML lint (including workflows), GitHub Actions validation with actionlint, an Ansible syntax check, and Ansible lint on a GitHub-hosted Ubuntu runner. It uses read-only repository permissions and requires no AWS credentials, private infrastructure repository, or self-hosted runner.

CI validates the source without running remediation. Convergence, audit service behavior, reboot handling, and idempotence still require manual testing on an Ubuntu 20.04 system. Record completed checks and any pending test-system validation in each PR.

From the repository root, reproduce the Python-based checks with Python 3.12:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r .ci/requirements.txt
export ANSIBLE_COLLECTIONS_PATH="$PWD/.ansible/collections"
export ANSIBLE_LOCAL_TEMP="$PWD/.ansible/tmp"
ansible-galaxy collection install -r .ci/collections.yml
yamllint --strict .
ansible-playbook --syntax-check -i localhost, site.yml
ansible-lint --offline site.yml
```

The CI workflow also validates its own syntax with actionlint; its version and checksum are recorded in the workflow. CI dependencies are pinned in `.ci/` and are separate from the role's runtime collection requirements. Commit signatures and sign-off are reviewed by maintainers.

## Distribution

Install this community role directly from [this Git repository](https://github.com/karlg100/UBUNTU20-STIG), selecting a reviewed commit or release. For example, use this role entry in an Ansible Galaxy requirements file, replacing `devel` with the commit or release you have validated:

```yaml
roles:
  - name: ubuntu20_stig
    src: https://github.com/karlg100/UBUNTU20-STIG.git
    scm: git
    version: devel
```

Run `ansible-galaxy role install -r requirements.yml`. Install the required collections separately; see the official [collection installation guide](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_installing.html). From a checkout of this role, the inherited collection manifest can be installed with:

```sh
ansible-galaxy collection install -r collections/requirements.yml
```

That manifest uses public collection Git repositories without version pins. For repeatable deployments, use your own collection requirements file with versions validated on your Ubuntu 20.04 test system. The pins in `.ci/collections.yml` define static CI checks and do not establish runtime compatibility.

The metadata identifies this fork as `karlg100.ubuntu20_stig`; that does not imply it has been published to Galaxy. The inherited automatic Galaxy publishing workflow has been removed. Any future Galaxy publication requires a verified community-owned namespace and an explicitly configured release process.

## Optional local hooks

After installing [pre-commit](https://pre-commit.com), run the configured hooks from the repository root:

```sh
pre-commit run --all-files
```

These include additional secret and formatting checks. They are separate from the checks run by Community CI.
