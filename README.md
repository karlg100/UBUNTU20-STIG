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

Community fixes land in this fork's [devel branch](https://github.com/karlg100/UBUNTU20-STIG/tree/devel). See [releases](https://github.com/karlg100/UBUNTU20-STIG/releases) for published versions. Use a reviewed commit from this repository when pinning a deployment.

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
- [Contributing changes](CONTRIBUTING.rst)
- [Issues](https://github.com/karlg100/UBUNTU20-STIG/issues) and [pull requests](https://github.com/karlg100/UBUNTU20-STIG/pulls)
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

## Testing

[Community CI](.github/workflows/ci.yml) runs on pull requests and pushes to `devel` and `main`, and can be started manually. It runs YAML lint (including workflows), GitHub Actions validation with actionlint, an Ansible syntax check, and Ansible lint on a GitHub-hosted Ubuntu runner. It uses read-only repository permissions and requires no AWS credentials, private infrastructure repository, or self-hosted runner.

CI validates the source without running remediation. Convergence, audit service behavior, reboot handling, and idempotence still require manual testing on an Ubuntu 20.04 system. Record completed checks and any pending test-system validation in each PR.

To reproduce the Python-based checks with Python 3.12:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r .ci/requirements.txt
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

Run `ansible-galaxy role install -r requirements.yml`. The metadata identifies this fork as `karlg100.ubuntu20_stig`; that does not imply it has been published to Galaxy. The inherited automatic Galaxy publishing workflow has been removed. Any future Galaxy publication requires a verified community-owned namespace and an explicitly configured release process.

## Added Extras

- [pre-commit](https://pre-commit.com) can be tested and can be run from within the directory

```sh
pre-commit run
```
