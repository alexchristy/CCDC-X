import pytest
from proxmoxer import ProxmoxAPI
from pytest_mock import MockerFixture

from library.proxmox_themed_vmid import gen_themed_vmid, get_vmids_in_range

###### gen_themed_vmid tests ######


def test_get_vmids_in_range_single_node(mocker: MockerFixture) -> None:
    """Test get_vmids_in_range with a single node."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Mock the return value of proxmox.nodes.get()
    mock_nodes = mocker.Mock()
    mock_nodes.get.return_value = [{"node": "node1"}]  # Simulate node list

    # Mock node1.qemu.get() to return VMIDs
    mock_node1 = mocker.Mock()
    mock_node1.qemu.get.return_value = [
        {"vmid": -1},
        {"vmid": 989},
        {"vmid": 990},
        {"vmid": 991},
        {"vmid": 992},
        {"vmid": 995},
        {"vmid": 996},
        {"vmid": 10167},
    ]

    # Attach the mock to the proxmox mock
    mock_proxmox.nodes = mock_nodes

    # Simulate proxmox.nodes("node1")
    mock_proxmox.nodes.side_effect = lambda n: (
        mock_node1 if n == "node1" else mock_nodes
    )

    # Test get_vmids_in_range
    existing_vmids = get_vmids_in_range(mock_proxmox, 990, 995)

    assert existing_vmids == [990, 991, 992, 995]

    # Verify calls
    mock_proxmox.nodes.get.assert_called_once()
    mock_proxmox.nodes.assert_called_with("node1")
    mock_node1.qemu.get.assert_called_once()


def test_get_vmids_in_range_no_vmids(mocker: MockerFixture) -> None:
    """Test get_vmids_in_range returns empty list when no vmids used in range."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Mock the return value of proxmox.nodes.get()
    mock_nodes = mocker.Mock()
    mock_nodes.get.return_value = [{"node": "node1"}]  # Simulate node list

    # Mock node1.qemu.get() to return VMIDs
    mock_node1 = mocker.Mock()
    mock_node1.qemu.get.return_value = [
        {"vmid": -1},
        {"vmid": 989},
        {"vmid": 996},
        {"vmid": 10167},
    ]

    # Attach the mock to the proxmox mock
    mock_proxmox.nodes = mock_nodes

    # Simulate proxmox.nodes("node1")
    mock_proxmox.nodes.side_effect = lambda n: (
        mock_node1 if n == "node1" else mock_nodes
    )

    # Test get_vmids_in_range
    existing_vmids = get_vmids_in_range(mock_proxmox, 990, 995)

    assert existing_vmids == []

    # Verify calls
    mock_proxmox.nodes.get.assert_called_once()
    mock_proxmox.nodes.assert_called_with("node1")
    mock_node1.qemu.get.assert_called_once()


def test_get_vmids_in_range_multiple_nodes(mocker: MockerFixture) -> None:
    """Test get_vmids_in_range with multiple nodes."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Mock the return value of proxmox.nodes.get() to return two nodes
    mock_nodes = mocker.Mock()
    mock_nodes.get.return_value = [
        {"node": "node1"},
        {"node": "node2"},
    ]  # Simulate multiple nodes

    # Mock node1.qemu.get() to return VMIDs
    mock_node1 = mocker.Mock()
    mock_node1.qemu.get.return_value = [
        {"vmid": 989},
        {"vmid": 991},
        {"vmid": 992},
        {"vmid": 995},
        {"vmid": 996},
    ]

    # Mock node2.qemu.get() to return a different set of VMIDs
    mock_node2 = mocker.Mock()
    mock_node2.qemu.get.return_value = [
        {"vmid": -1},
        {"vmid": 990},
        {"vmid": 993},
        {"vmid": 994},
        {"vmid": 997},
        {"vmid": 998},
    ]

    # Attach the mock to proxmox
    mock_proxmox.nodes = mock_nodes

    # Use a single lambda side_effect to handle multiple nodes
    mock_proxmox.nodes.side_effect = lambda n=None: (
        mock_node1 if n == "node1" else mock_node2 if n == "node2" else mock_nodes
    )

    # Test get_vmids_in_range
    existing_vmids = get_vmids_in_range(mock_proxmox, 990, 995)

    # Assert the result includes VMIDs from both nodes
    existing_vmids.sort()
    assert existing_vmids == [990, 991, 992, 993, 994, 995]

    # Verify calls
    mock_proxmox.nodes.get.assert_called_once()
    mock_proxmox.nodes.assert_any_call("node1")
    mock_proxmox.nodes.assert_any_call("node2")
    mock_node1.qemu.get.assert_called_once()
    mock_node2.qemu.get.assert_called_once()


def test_get_vmids_in_range_skip_node_on_exception(mocker: MockerFixture) -> None:
    """Test get_vmids_in_range skips nodes that throw exceptions."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Mock the return value of proxmox.nodes.get() to return two nodes
    mock_nodes = mocker.Mock()
    mock_nodes.get.return_value = [
        {"node": "node1"},
        {"node": "node2"},
        {"node": "node3"},
    ]  # Simulate multiple nodes

    # Mock node1.qemu.get() to return VMIDs successfully
    mock_node1 = mocker.Mock()
    mock_node1.qemu.get.return_value = [
        {"vmid": 991},
        {"vmid": 992},
    ]

    # Mock node2.qemu.get() to raise an exception
    mock_node2 = mocker.Mock()
    mock_node2.qemu.get.side_effect = Exception("QEMU error on node2")

    # Mock node3.qemu.get() to return VMIDs successfully
    mock_node3 = mocker.Mock()
    mock_node3.qemu.get.return_value = [
        {"vmid": 994},
        {"vmid": 995},
    ]

    # Attach the mock to proxmox
    mock_proxmox.nodes = mock_nodes

    # Use a dictionary for side_effect to return the correct mock based on node name
    mock_proxmox.nodes.side_effect = lambda n=None: {
        "node1": mock_node1,
        "node2": mock_node2,
        "node3": mock_node3,
    }.get(n, mock_nodes)

    # Test get_vmids_in_range
    existing_vmids = get_vmids_in_range(mock_proxmox, 990, 995)

    # Assert the result includes VMIDs from node1 and node3, but skips node2
    assert existing_vmids == [991, 992, 994, 995]

    # Verify calls
    mock_proxmox.nodes.get.assert_called_once()
    mock_proxmox.nodes.assert_any_call("node1")
    mock_proxmox.nodes.assert_any_call("node2")
    mock_proxmox.nodes.assert_any_call("node3")
    mock_node1.qemu.get.assert_called_once()
    mock_node3.qemu.get.assert_called_once()
    mock_node2.qemu.get.assert_called_once()  # Ensure it was called but threw an exception


###### gen_themed_vmid tests ######


def test_gen_themed_vmid_long_netmask_exception(mocker: MockerFixture) -> None:
    """Test gen_themed_vmid raises an exception for netmasks longer than the reference VMID."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Test gen_themed_vmid with a netmask longer than 3
    with pytest.raises(ValueError) as e:
        gen_themed_vmid(mock_proxmox, 990, 4, 3)

    assert "exceed" in str(e.value).lower()


def test_gen_themed_vmid(mocker: MockerFixture) -> None:
    """Test gen_tehemd_vmid generates themed VMIDs under common scenarios."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Mock get_vmids_in_range to return sample VMIDs
    mock_get_vmids_in_range = mocker.patch(
        "library.proxmox_themed_vmid.get_vmids_in_range"
    )
    mock_get_vmids_in_range.return_value = [990, 991, 992, 993, 994, 995]

    # Test gen_themed_vmid with a reference VMID of 990 and a netmask length of 2
    themed_vmids = gen_themed_vmid(mock_proxmox, 990, 2, 3)

    # Assert the result is the next available themed VMIDs
    themed_vmids.sort()
    assert themed_vmids == [996, 997, 998]

    # Verify calls
    mock_get_vmids_in_range.assert_called_once_with(mock_proxmox, 990, 999)


def test_gen_themed_vmid_not_enough_available(mocker: MockerFixture) -> None:
    """Test gen_themed_vmid raises an exception when not enough VMIDs are available in the themed range."""
    # Mock ProxmoxAPI
    mock_proxmox = mocker.MagicMock(spec=ProxmoxAPI)

    # Mock get_vmids_in_range to return sample VMIDs
    mock_get_vmids_in_range = mocker.patch(
        "library.proxmox_themed_vmid.get_vmids_in_range"
    )
    mock_get_vmids_in_range.return_value = [990, 991, 992, 993, 994, 995, 996, 997, 998]

    # Test gen_themed_vmid with a reference VMID of 990 and a netmask length of 2
    # Requesting 3 VMIDs, but only 1 is available
    with pytest.raises(ValueError) as e:
        gen_themed_vmid(mock_proxmox, 990, 2, 3)

    assert "no available" in str(e.value).lower()
    assert "990-999" in str(e.value)  # Themed range included in error message

    # Verify calls
    mock_get_vmids_in_range.assert_called_once_with(mock_proxmox, 990, 999)
