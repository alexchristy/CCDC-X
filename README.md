# CCDC-X
Welcome to the 202X CCDC competition. Generate new CCDC style networks on the fly.

## Quickstart 

Follow the steps below to setup the configure the project and run playbooks right away.

1) Create Python virtual environment

    ```bash
    python3 -m venv venv
    ```

2) Activate virtual environment

    ```bash
    source venv/bin/activate
    ```

3) Install all Python dependencies

    ```bash
    pip install -r requirements.txt
    ```

4) Install Ansible dependencies

    ```bash
    ansible-galaxy install -r requirements.yml
    ```

5) Configure C2 machine

    ```bash
    ansible-playbook ./setup.yml
    ```

6) Configure `inventory/hosts.ini`. *Example:*

    ```ini
    [linux_hosts]
    dns_main ansible_host=1.1.1.1

    [linux_hosts:vars]
    ansible_user="ubuntu"
    ansible_ssh_private_key_file="/path/to/private/key.pem"
    ansible_become=true
    ansible_become_method=sudo
    ```

7) Run a playbook. *Example: Adding misconfigured users to a system.*

    ```bash
    ansible-playbook -i inventory/hosts.ini playbooks/user_setup.yml
    ```

## Playbooks

All playbooks are in `playbooks/`.

1) `gen_random_ccdc.yml`

    This playbook will create linked clones a series of randomly chosen VMs from a node's templates. Requires a single argument `ref_vmid` which tells the playbook what pattern VMIDs should follow.

    With the current configuration running the example command below, the playbook will clone and create 5 VM clones with the VMIDs: 666000, 666001, 666002, 666003, 666004 assumming
    the VMIDs are available. If not it will find and assign VMIDs that are available in that theme.

    All VMs are named with the `network_name` prefixed.

    **Details:**
    - Targets: `proxmox_nodes`
    - Variable Files:
        - `proxmox.yml` (vault)
        - `network.yml`

    **Example:**
    ```bash
    ansible-playbook -i inventory/hosts.ini playbooks/gen_random_ccdc.yml --ask-vault-pass -e "ref_vmid=666000"
    ```

2) `teardown_network.yml`

    This playbook deletes all VMs that are prefixed with the `network_name` value.

    **Details:**
    - Targets: `proxmox_nodes`
    - Variable Files:
        - `proxmox.yml` (vault)
        - `network.yml`

    **Example:**
    ```bash
    ansible-playbook -i invenvtory/hosts.ini playbooks/gen_random_ccdc.yml --ask-vault-pass
    ```

3)  `user_setup.yml`

    This playbook handles creating all the common user misconfigurations seen in a CCDC-style competition. To see the current capabilities of this playbook see [PROGRESS.md](./PROGRESS.md) and the `user_setup` role's [main.yml](./roles/user_setup/tasks/main.yml) for an overview.

    **Details:**
    - Targets: `linux_hosts`
    - Variable Files:
        - `linux_vm_config.yml`
        - `generated_assets_config.yml`

    **Example:** *Add UID 0 (root users) and obfuscate the added accounts.*
    ```bash
    ansible-playbook -i inventory/hosts.ini playbooks/user_setup.yml --tags uid0,obfuscation
    ```


## Development Setup

1) Create Python virtual environment

    ```bash
    python3 -m venv venv
    ```

2) Activate virtual environment

    ```bash
    source venv/bin/activate
    ```

3) Install all Python dependencies

    ```bash
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
    ```

4) Install Ansible dependencies

    ```bash
    ansible-galaxy install -r requirements.yml
    ```

5) Configure project

    ```bash
    ansible-playbook setup.yml
    ```