# Community support

This Ubuntu 20.04 STIG role is maintained as an independent community fork of [ansible-lockdown/UBUNTU20-STIG](https://github.com/ansible-lockdown/UBUNTU20-STIG). MindPoint Group no longer maintains this role.

Support and contribution channels are hosted in **karlg100/UBUNTU20-STIG**:

- [Questions and help](https://github.com/karlg100/UBUNTU20-STIG/issues/new): describe the configuration and behavior you need help with.
- [Bug reports and feature requests](https://github.com/karlg100/UBUNTU20-STIG/issues): check existing issues first, then open a new report if needed.
- [Proposed changes](https://github.com/karlg100/UBUNTU20-STIG/pulls): submit a pull request targeting this repository's `devel` branch and link the relevant issue.

## Reporting a problem

Include the role branch and commit, Ubuntu and Ansible versions, relevant control IDs or task names, and the settings needed to reproduce the problem. Describe the expected and observed behavior. For idempotence reports, distinguish the first convergence from the repeat run and identify which tasks still report changed.

Share only the relevant, sanitized output. Remove credentials, private keys, tokens, and sensitive host or audit-record contents before posting.

## Contributing a fix

Use a separate branch, GPG-sign and sign off your commits, and describe the validation performed in the pull request. State which checks passed and which test-system checks remain pending. See the [README contribution guidance](README.md#community-contribution) and the [issue tracker](https://github.com/karlg100/UBUNTU20-STIG/issues) for current work.
