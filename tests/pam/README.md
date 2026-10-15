# Native Ubuntu 20.04 PAM regression tests

These tests execute the actual tagged UBTU-20-010072 control through Ansible's
Docker connection. The target uses packaged Focal `libpam-runtime` and
`libpam-modules`, including the unmodified `pam-auth-update` generator.
One separate fault-injection case wraps that generator to test rollback after
it writes its output but returns failure.

The harness requires a disposable container with the test label and no host
mounts. It resets PAM configuration and the container's debconf database between
tests. **Never run it against a real host or a container carrying useful state.**
The test controller can be a Linux or macOS machine with Docker available.

From the repository root, after installing `.ci/requirements.txt` and
`.ci/collections.yml` in an isolated controller environment:

```sh
docker run --detach --platform linux/amd64 --name stig-pam-tests \
  --label codex.task=ubuntu20-pam-issue16 \
  ubuntu:20.04@sha256:8feb4d8ca5354def3d8fce243717141ce31e2c428701f6682bd2fafe15388214 \
  sleep infinity
docker exec --env DEBIAN_FRONTEND=noninteractive stig-pam-tests apt-get update
docker exec --env DEBIAN_FRONTEND=noninteractive stig-pam-tests \
  apt-get install --yes --no-install-recommends python3 libpam-runtime libpam-modules
python tests/pam/test_faillock.py --container stig-pam-tests
docker rm --force stig-pam-tests
```

The harness records the PAM package versions, generator SHA256 and controller
version. CI uses the same entry point and removes its container even on failure.

Coverage includes clean and partial role-owned configurations, explicit
migration from overlapping selected families, disabled/no-migration no-ops,
unrelated profile preservation, spacing/options differences, distinct PAM
controls, incomplete targets, customized legacy profiles, unattributed generated
entries, unseen defaults, profile conflicts, native refusal of local modifications,
failure rollback, check mode, and idempotent repeats before and after a later
`pam-auth-update` regeneration.

This is native configuration-generation testing, not full-role Molecule, a VM
boot test, or login/lockout acceptance. It does not test authentication through
SSH, a display manager, directory services, or smart cards.
