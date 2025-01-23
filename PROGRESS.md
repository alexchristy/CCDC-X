# PROGRESS.md

This is a living document that will list all existing and planned features and capabilities for the different playbooks in this project.

## user_setup.yml

- [x] UID 0 users (extra root users)
- [x] Regular users
    - [x] Randomized SSH Keys
    - [ ] Randomized single user full sudo privileges
    - [ ] Randomized sudo group membership
    - [ ] Randomized disguised login shell
    - [ ] Randomized SSH Keys in unconventional location (Random location not `~/.ssh`)
    - [ ] Randomized protected SSH keys (SSH keys that can't be removed)
- [ ] Single user full sudo permissions
    - [ ] /etc/sudoers
    - [ ] /etc/sudoers.d/
- [ ] Groups with full sudo privileges
    - [ ] /etc/sudoers
    - [ ] /etc/sudoers.d/
- [x] Fudged system users (accounts disguised as existing system accounts)
    - [ ] Randomized SSH Keys in unconventional location (Random location not `~/.ssh`)
    - [ ] Randomized single user full sudo privileges
    - [ ] Randomized sudo group membership
    - [ ] Randomized disguised login shell
- [ ] Tweaked system users (existing system users)
    - [ ] Randomized disguised login shell
    - [ ] Randomized SSH Keys in unconventional location (Random location not `~/.ssh`)
- [ ] Permit SSH root login
- [ ] Enable SSH cleartext password authentication
- [x] Scoring user
    - [x] SSH key
    - [ ] Single user full sudo privileges
- [x] Blueteam user
    - [x] SSH key
    - [ ] Single user full sudo privileges
- [ ] Disguised login shell binaries
    - [ ] /bin/nologin
    - [ ] /bin/false
    - [ ] /bin/true
    - [ ] /bin/rbash

