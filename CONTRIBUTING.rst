Contributing to the Ubuntu 20.04 STIG Community Fork
====================================================

Use this repository's `issues <https://github.com/karlg100/UBUNTU20-STIG/issues>`_
for questions, bug reports, and feature requests. Submit pull requests to
``karlg100/UBUNTU20-STIG:devel``. Contributions are maintained here independently
of MindPoint Group; no upstream staging branch or infrastructure is required.

Rules
-----
1) GPG-sign all commits intended for merge.
2) Include a Signed-off-by trailer in each contribution commit.
3) Work in a separate branch and link the relevant fork issue.
4) Record completed validation and any test-system checks still pending.
5) Be respectful of other contributors.

Preparing a change
------------------
Start a topic branch from this repository's ``devel`` branch. Contributors
without write access can fork ``karlg100/UBUNTU20-STIG`` and submit their branch
here. Use the issue tracker and pull request target above rather than the
original Ansible Lockdown repository.

Keep a pull request focused on one problem and link its fork issue. Describe
the current behavior, the change, and any affected control IDs or variables.
Preserve the original license and attribution. Keep public variable names and
control identifiers compatible unless the change explicitly requires otherwise;
explain configuration changes that existing deployments will need.

Validation
----------
The community CI workflow runs YAML lint, GitHub Actions validation, Ansible
syntax checks, and Ansible lint on GitHub-hosted runners. It uses read-only
repository permissions and does not run remediation or provision test systems.

Commit signatures and sign-off are reviewed by maintainers; the workflow does
not claim to enforce them. Functional convergence and idempotence must be
validated separately on an Ubuntu 20.04 test system. Include those results, or
clearly mark them pending, in the pull request. See `README.md <README.md#testing>`_
for local setup and validation commands. Run them from the repository root;
``site.yml`` runs remediation unless a non-executing option such as
``--syntax-check`` is specified.

For behavior changes, record the role commit, controller and collection versions,
Ubuntu version, relevant settings, and expected results. Apply the role to a
representative test system, verify the resulting configuration, and repeat with
the same inputs to assess idempotence. Explain any tasks that still report
changed or failed. Share sanitized results, following `SUPPORT.md <SUPPORT.md>`_.

When updating dependencies, review the pins in ``.ci/`` and the relevant
``.pre-commit-config.yaml`` hooks together. Runtime dependencies are declared
separately in ``collections/requirements.yml`` and ``meta/main.yml``; passing
static CI does not qualify a dependency version for deployment. Keep third-party
GitHub Actions pinned to full commit IDs and update downloaded-tool checksums
when changing versions.

Signing your contribution
-------------------------

We've chosen to use the Developer's Certificate of Origin (DCO) method
that is employed by the Linux Kernel Project, which provides a simple
way to contribute to this community fork.

The process is to certify the DCO 1.1 text below::

    Developer's Certificate of Origin 1.1

    By making a contribution to this project, I certify that:

    (a) The contribution was created in whole or in part by me and I
        have the right to submit it under the open source license
        indicated in the file; or

    (b) The contribution is based upon previous work that, to the best
        of my knowledge, is covered under an appropriate open source
        license and I have the right under that license to submit that
        work with modifications, whether created in whole or in part
        by me, under the same open source license (unless I am
        permitted to submit under a different license), as indicated
        in the file; or

    (c) The contribution was provided directly to me by some other
        person who certified (a), (b) or (c) and I have not modified
        it.

    (d) I understand and agree that this project and the contribution
        are public and that a record of the contribution (including all
        personal information I submit with it, including my sign-off) is
        maintained indefinitely and may be redistributed consistent with
        this project or the open source license(s) involved.

Then, when it comes time to submit a contribution, include the
following text in your contribution commit message::

   Signed-off-by: Joan Doe <joan.doe@example.com>

This message can be entered manually, or if you have configured git
with the correct ``user.name`` and ``user.email``, you can use the ``-s``
option to ``git commit`` to automatically include the signoff message.

Use ``git commit -S -s`` to sign the commit and add the sign-off trailer.
