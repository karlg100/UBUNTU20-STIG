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

Workflow
--------
The community CI workflow runs YAML lint, GitHub Actions validation, Ansible
syntax checks, and Ansible lint on GitHub-hosted runners. It uses read-only
repository permissions and does not run remediation or provision test systems.

Commit signatures and sign-off are reviewed by maintainers; the workflow does
not claim to enforce them. Functional convergence and idempotence must be
validated separately on an Ubuntu 20.04 test system. Include those results, or
clearly mark them pending, in the pull request. See `README.md <README.md#testing>`_
for the local validation commands.

Signing your contribution
-------------------------

We've chosen to use the Developer's Certificate of Origin (DCO) method
that is employed by the Linux Kernel Project, which provides a simple
way to contribute to this community fork.

The process is to certify the below DCO 1.1 text
::

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
::

Then, when it comes time to submit a contribution, include the
following text in your contribution commit message:

::

   Signed-off-by: Joan Doe <joan.doe@email.com>

::

This message can be entered manually, or if you have configured git
with the correct `user.name` and `user.email`, you can use the `-s`
option to `git commit` to automatically include the signoff message.

Use ``git commit -S -s`` to sign the commit and add the sign-off trailer.
