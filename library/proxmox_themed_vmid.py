#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Alex Christy (@alexchristy) <christya2ATgmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = """
---
module: proxmox_themed_vmid
short_description: Generate the next available VMIDs in a themed range for Proxmox VE
description:
  - This module generates the next available VMIDs within a specific range, defined by a reference VMID and netmask length.
  - Useful for maintaining logical VMID allocations based on network or project themes.
  - Ensures global uniqueness of VMIDs across Proxmox cluster nodes by dynamically querying all nodes.
version_added: "1.0.0"
author:
  - Alex Christy (@alexchristy)
options:
  api_host:
    description:
      - The Proxmox VE API host to connect to.
    required: true
    type: str
  api_user:
    description:
      - The Proxmox VE user with API access permissions.
    required: true
    type: str
  api_password:
    description:
      - The password for authenticating the Proxmox VE user.
    required: true
    type: str
    no_log: true
  verify_ssl:
    description:
      - Whether to verify SSL certificates for API communication.
    required: false
    default: false
    type: bool
  router_vmid:
    description:
      - Router VMID used to connect VMs to the same network.
    required: true
    type: int
  netmask_len:
    description:
      - The number of digits from the reference VMID defining the network ID.
    required: true
    type: int
  num:
    description:
      - The number of VMIDs to generate.
    required: false
    default: 1
    type: int
requirements:
  - "python >= 3.10.12"
  - "proxmoxer >= 2.2.0"
notes:
  - Ensure the API user has sufficient privileges to query VM information across all nodes.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action_group:
    version_added: 2.0.0
"""

EXAMPLES = """
- name: Generate themed VMID for project
  proxmox_themed_vmid:
    api_host: "proxmox.local"
    api_user: "root@pam"
    api_password: "secret"
    router_vmid: 111003
    netmask_len: 3
    num: 2
  register: result

- name: Debug generated VMID
  ansible.builtin.debug:
    msg: "Next available themed VMIDs: {{ result.themed_vmids }}"

- name: Perform task on each VMID
  ansible.builtin.debug:
    msg: "Working with VMID {{ item }}"
  loop: "{{ result.themed_vmids }}"

"""

RETURN = """
themed_vmids:
  description: A list of the next available VMIDs within the themed range.
  returned: success
  type: list
  elements: int
  sample: [111004, 111005, 111006]
msg:
  description: A descriptive message regarding the VMID generation process.
  returned: always
  type: str
  sample: "Next available VMIDs: [111004, 111005, 111006]"
"""

import logging

from ansible.module_utils.basic import AnsibleModule
from proxmoxer import ProxmoxAPI

logger = logging.getLogger(__name__)


def get_vmids_in_range(
    proxmox: ProxmoxAPI, themed_min_vmid: int, themed_max_vmid: int
) -> list[int]:
    """Retrieve all VMIDs within a specific range across all nodes.

    Args:
    ----
        proxmox (ProxmoxAPI): Proxmox API object.
        themed_min_vmid (int): Minimum VMID in the themed range.
        themed_max_vmid (int): Maximum VMID in the themed range.

    Returns:
    -------
        list[int]: List of VMIDs within the specified range across all nodes.

    """
    existing_vmids = []
    nodes = proxmox.nodes.get()  # Get list of nodes in the Proxmox cluster
    logger.debug(
        "Retrieved nodes from Proxmox API: %s", [node["node"] for node in nodes]
    )

    for node in nodes:
        try:
            # Retrieve VMIDs from each node and add them to the list if in the range
            vms = proxmox.nodes(node["node"]).qemu.get()
            node_vmids = [
                vm["vmid"]
                for vm in vms
                if themed_min_vmid <= vm["vmid"] <= themed_max_vmid
            ]
            existing_vmids.extend(node_vmids)
            logger.debug("Node %s: VMIDs in themed range: %s", node["node"], node_vmids)
        except Exception as e:
            logger.warning("Failed to retrieve VMIDs from node %s: %s", node["node"], e)

    return existing_vmids


def gen_themed_vmid(
    proxmox: ProxmoxAPI, reference_vmid: int, netmask_len: int, num: int = 1
) -> list[int]:
    """Generate the next available VMIDs within a themed range based on a reference VMID and netmask_len.

    Args:
    ----
        proxmox (ProxmoxAPI): Proxmox API object for querying existing VMIDs.
        reference_vmid (int): A VMID that indicates the network theme (e.g., 111003).
        netmask_len (int): Number of digits defining the network ID counting from the left. (e.g. netmask_len=3, reference_vmid=111002 --> Network ID: 111).
        num (int): Number of VMIDs to generate (default: 1).

    Returns:
    -------
        int: The next available VMID within the themed range.

    Raises:
    ------
        ValueError: If no available VMID is found within the themed range.

    """
    # Convert the reference VMID to a string for processing
    reference_vmid_str = str(reference_vmid)

    # Calculate the network ID length and host ID length
    vmid_length = len(reference_vmid_str)
    host_id_length = vmid_length - netmask_len
    if host_id_length <= 0:
        msg = f"Netmask length value: {netmask_len} exceeds the length of the reference VMID (len: {vmid_length})."
        raise ValueError(msg)

    network_id = reference_vmid_str[:netmask_len]  # Extract network part

    # Calculate the min and max VMID in the themed range based on the network ID
    themed_min_vmid = int(f"{network_id}{'0' * host_id_length}")
    themed_max_vmid = int(f"{network_id}{'9' * host_id_length}")
    logger.info(
        "Searching for available VMID within range %d-%d",
        themed_min_vmid,
        themed_max_vmid,
    )

    # Retrieve existing VMIDs within the themed range
    existing_vmids = get_vmids_in_range(proxmox, themed_min_vmid, themed_max_vmid)
    existing_vmids.sort()

    # Find the next available VMID within the range
    gened_vmids: list[int] = []
    for _ in range(num):
        found_vmid = False
        for vmid in range(themed_min_vmid, themed_max_vmid + 1):
            if vmid not in existing_vmids:
                logger.info("Next available VMID: %d", vmid)
                existing_vmids.append(vmid)  # Prevent selecting the same VMID again
                gened_vmids.append(vmid)
                found_vmid = True
                break

        if found_vmid:
            continue

        # Log an error and raise an exception if no VMID is available in the themed range
        logger.error(
            "No available VMID found in the themed range %d-%d.",
            themed_min_vmid,
            themed_max_vmid,
        )
        msg = f"No available VMID found in the themed range {themed_min_vmid}-{themed_max_vmid}."
        raise ValueError(msg)

    return gened_vmids


def run() -> None:  # pragma: no cover
    """Run the custom Ansible module."""
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type="str", required=True),
            api_user=dict(type="str", required=True),
            api_password=dict(type="str", required=True, no_log=True),
            verify_ssl=dict(type="bool", required=False, default=False),
            router_vmid=dict(type="int", required=True),
            netmask_len=dict(type="int", required=True),
            num=dict(type="int", required=False, default=1),
        )
    )

    # Connect to proxmox API
    try:
        proxmox_api = ProxmoxAPI(
            module.params["api_host"],
            user=module.params["api_user"],
            password=module.params["api_password"],
            verify_ssl=False,
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to connect to Proxmox API: {e}")

    # Generate the next available VMID within the themed range
    try:
        themed_vmids = gen_themed_vmid(
            proxmox_api,
            reference_vmid=module.params["router_vmid"],
            netmask_len=module.params["netmask_len"],
            num=module.params["num"],
        )
    except ValueError as e:
        module.fail_json(msg=str(e))

    result = {
        "changed": False,
        "msg": f"Next available themed VMIDs: {themed_vmids}",
        "themed_vmids": themed_vmids,
    }

    module.exit_json(**result)


if __name__ == "__main__":  # pragma: no cover
    run()
