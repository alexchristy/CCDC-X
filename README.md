# CCDC-X
Welcome to the 202X CCDC competition. Generate new CCDC style networks on the fly.

## Playbooks

All playbooks are in `playbooks/`.

1) `gen_random_ccdc.yml`

    This playbook will create linked clones a series of randomly chosen VMs from a node's templates. Requires a single argument `ref_vmid` which tells the playbook what pattern VMIDs should follow.

    With the current configuration running the example command below, the playbook will clone and create 5 VM clones with the VMIDs: 666000, 666001, 666002, 666003, 666004 assumming
    the VMIDs are available. If not it will find and assign VMIDs that are available in that theme.

    All VMs are named with the `network_name` prefixed.

    **Example:**
    ```bash
    ansible-playbook -i inventory/hosts.ini playbooks/gen_random_ccdc.yml --ask-vault-pass -e "ref_vmid=666000"
    ```

2) `teardown_network.yml`

    This playbook deletes all VMs that are prefixed with the `network_name` value.

    **Example:**
    ```bash
    ansible-playbook -i invenvtory/hosts.ini playbooks/gen_random_ccdc.yml --ask-vault-pass
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