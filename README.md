# Ubuntu 20.04 DISA STIG — Community Fork

This repository is a community-maintained fork of [ansible-lockdown/UBUNTU20-STIG](https://github.com/ansible-lockdown/UBUNTU20-STIG). MindPoint Group no longer maintains the Ubuntu 20.04 role. Maintenance and contributions continue independently in [karlg100/UBUNTU20-STIG](https://github.com/karlg100/UBUNTU20-STIG).

The original work by MindPoint Group / Ansible Lockdown and its contributors remains credited. The [MIT license and original copyright notice](LICENSE) are preserved.

## Configure a Ubuntu 20.04 system to be [DISA STIG](https://public.cyber.mil/stigs/downloads/) compliant.

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

Check Mode is not supported! The role will complete in check mode without errors, but it is not supported and should be used with caution.

This role was developed against a clean install of the Ubuntu 20 operating system. If you are implementing to an existing system please review this role for any site specific changes that are needed.

Community fixes land in this fork's [devel branch](https://github.com/karlg100/UBUNTU20-STIG/tree/devel). No community release has been published yet. Use a reviewed commit from this repository when pinning a deployment.

---

## Matching a security Level for STIG

It is possible to to only run controls that are based on a particular for security level for STIG.
This is managed using tags:

- CAT1
- CAT2
- CAT3

The control found in defaults main also need to reflect true so as this will allow the controls to run when the playbook is launched.

## Coming from a previous release

STIG releases always contain changes, it is highly recommended to review the new references and available variables. This has changed significantly since the initial release of ansible-lockdown.
This is now compatible with python3 if it is found to be the default interpreter. This does come with pre-requisites which it configures the system accordingly.

Further details can be seen in the [Changelog](./ChangeLog.md)

## Auditing (new)

Currently this release does not have a auditing tool.

## Documentation

- [Community support and reporting problems](SUPPORT.md)
- [Requirements](#requirements)
- [Role variables and customization](#role-variables), with available settings in [defaults/main.yml](defaults/main.yml)
- [Control selection with tags](#tags)
- [Contributing changes](#community-contribution)
- [Maintenance status](#maintenance-status)
- [Change history](ChangeLog.md)

## Requirements

**General:**

- Basic knowledge of Ansible, below are some links to the Ansible documentation to help get started if you are unfamiliar with Ansible

  - [Main Ansible documentation page](https://docs.ansible.com)
  - [Ansible Getting Started](https://docs.ansible.com/ansible/latest/user_guide/intro_getting_started.html)
  - [Tower User Guide](https://docs.ansible.com/ansible-tower/latest/html/userguide/index.html)
  - [Ansible Community Info](https://docs.ansible.com/ansible/latest/community/index.html)
- Functioning Ansible and/or Tower Installed, configured, and running. This includes all of the base Ansible/Tower configurations, needed packages installed, and infrastructure setup.
- Please read through the tasks in this role to gain an understanding of what each control is doing. Some of the tasks are disruptive and can have unintended consiquences in a live production system. Also familiarize yourself with the variables in the defaults/main.yml file.

**Technical Dependencies:**

- Ubuntu 20 - Other versions are not supported.
- Other OSs can be checked by changing the skip_os_check to true for testing purposes.
- python2-passlib (or just passlib, if using python3)
- python-lxml
- python-xmltodict

Package 'python-xmltodict' is required if you enable the OpenSCAP tool installation and run a report. Packages python(2)-passlib are required for tasks with custom filters or modules. These are all required on the controller host that executes Ansible.

## Role Variables

This role is designed that the end user should not have to edit the tasks themselves. All customizing should be done via the defaults/main.yml file or with extra vars within the project, job, workflow, etc. Non-disruptive CAT I, CAT II, and CAT III findings will be corrected by default. Disruptive finding remediation can be enabled by setting `ubtu20stig_disruption_high` to `true`.

## Tags

There are many tags available for added control precision. Each control may have it's own set of tags noting what level, if it's scored/notscored, what OS element it relates to, if it's a patch or audit, and the rule number.

Below is an example of the tag section from a control within this role. Using this example if you set your run to skip all controls with the tag CCI-002824, this task will be skipped. The opposite can also happen where you run only controls tagged with CCI-002824.

```sh
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

Contributions to this community fork are welcome.

- Work in a separate branch and submit pull requests to `karlg100/UBUNTU20-STIG:devel`.
- GPG-sign and sign off commits intended for merge.
- Link the relevant fork issue and describe the problem, fix, and validation performed.
- Record the checks that passed and any test-system validation still pending. For behavior changes, include an appropriate functional test and repeat-run results when available.
- Community releases will be documented separately when available.

## Maintenance status

| Issue | Work | Status | Commit / branch |
|---|---|---|---|
| [#1](https://github.com/karlg100/UBUNTU20-STIG/issues/1) | Honor the PAM control disable flag | Open; proposed fix | Pending |
| [#2](https://github.com/karlg100/UBUNTU20-STIG/issues/2) | Gate reboot on actual need | Open; proposed fix | Pending |
| [#3](https://github.com/karlg100/UBUNTU20-STIG/issues/3) | Report audit-rule changes accurately | Merged in [PR #6](https://github.com/karlg100/UBUNTU20-STIG/pull/6); manual test-system results pending | [2c10d88e](https://github.com/karlg100/UBUNTU20-STIG/commit/2c10d88ea3779b1b9e9dd5605ddcf5aeb63cc21b) on [fix/68-audit-rule-idempotence](https://github.com/karlg100/UBUNTU20-STIG/tree/fix/68-audit-rule-idempotence) |
| [#4](https://github.com/karlg100/UBUNTU20-STIG/issues/4) | Add a configurable two-hour APT cache interval | Open; proposed fix | Pending |
| [#5](https://github.com/karlg100/UBUNTU20-STIG/issues/5) | Investigate repeated audit-log metadata repairs | Open; producer of metadata changes unconfirmed | Pending |

The audit fix is included in `devel` through merge commit [f30d7eb7](https://github.com/karlg100/UBUNTU20-STIG/commit/f30d7eb76074b25494a06c68588c79760d669b30). Its isolated regressions, syntax checks, and targeted lint passed; these checks do not replace testing on an Ubuntu 20.04 system.

## Testing

The inherited GitHub workflows refer to the original project's self-hosted runner and AWS test infrastructure. Their presence does not establish that this fork has run those pipelines. Check each pull request for its actual validation results.

For role changes, document syntax and lint checks, relevant isolated regression checks, and manual convergence/idempotence results from an Ubuntu 20.04 test system. Clearly identify checks that remain pending.

## Added Extras

- [pre-commit](https://pre-commit.com) can be tested and can be run from within the directory

```sh
pre-commit run
```
