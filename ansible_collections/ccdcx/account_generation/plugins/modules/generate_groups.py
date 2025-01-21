import random

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ccdcx.account_generation.plugins.module_utils.random_utils import (
    random_whole_divide,
)

DEPT_GROUPS = [
    "hr",
    "finance",
    "marketing",
    "sales",
    "it",
    "legal",
    "engineering",
    "ops",  # Operations
    "support",
    "logistics",
    "compliance",
    "procurement",
    "training",
    "research",
    "admin",
    "security",
    "network_ops",
    "cloud_ops",
    "infra",
    "dev",
    "qa",
    "customer_success",
    "biz_dev",
    "payroll",
    "audit",
    "product",
    "design",
    "ux",
    "data_science",
    "analytics",
    "media",
    "recruiting",
    "benefits",
    "insurance",
    "facilities",
    "distribution",
    "inventory",
    "accounting",
    "tax",
    "helpdesk",
    "enterprise_apps",
    "vendor_mgmt",  # Vendor Management
    "gov_relations",
    "board",
    "executive",
    "c_suite",
    "training_dev",
    "quality_ctrl",  # Quality Control
    "field_ops",  # Field Operations
    "partnerships",
    "contract_mgmt",  # Contract Management
]

DEPT_GROUP_MODIFIERS = [
    "admin",
    "team",
    "support",
    "lead",
    "manager",
    "staff",
    "analyst",
    "specialist",
    "consultant",
    "intern",
    "assistant",
    "director",
    "vp",
    "chief",
    "planner",
    "auditor",
    "trainer",
    "advisor",
    "rep",  # Representative
    "exec",  # Executive
    "partner",
    "liaison",
    "advocate",
    "officer",
    "contractor",
    "leadership",
    "program",
    "services",
    "planning",
    "projects",
    "design",
    "rev",  # Review
    "scheduler",
    "mon",  # Monitor
    "control",
    "policy",
    "eval",  # Evaluation
    "data",
    "reporting",
    "comm",  # Communications
    "relations",
    "initiatives",
    "oversight",
    "admin_ops",
    "field",
    "dev",  # Developement
    "exec",  # Execution
    "oversight",
    "governance",
]


APP_PREFIXES = [
    "db",
    "web",
    "app",
    "api",
    "dev",
    "qa",
    "ci",
    "cd",
    "git",
    "svn",
    "mysql",
    "pgsql",
    "oracle",
    "mongo",
    "redis",
    "elk",
    "kafka",
    "zabbix",
    "prom",
    "graf",
    "jira",
    "confl",
    "slack",
    "zoom",
    "teams",
    "ad",
    "ldap",
    "idm",
    "auth",
    "sso",
    "dns",
    "mail",
    "smtp",
    "imap",
    "pop3",
    "ftp",
    "sftp",
    "vpn",
    "proxy",
    "firewall",
    "ids",
    "ips",
    "siem",
    "av",
    "edr",
    "ngfw",
    "waf",
    "nginx",
    "apache",
    "haproxy",
    "loadbal",
    "cloud",
    "aws",
    "azure",
    "gcp",
    "vmware",
    "vcenter",
    "vbox",
    "docker",
    "k8s",
    "openshift",
    "helm",
    "vault",
    "ansible",
    "puppet",
    "chef",
    "salt",
    "jenkins",
    "gitlab",
    "circleci",
    "travis",
    "terraform",
    "packer",
    "grafana",
    "splunk",
    "datadog",
    "newrelic",
    "sumologic",
    "airflow",
    "snowflake",
    "tableau",
    "powerbi",
    "looker",
    "sas",
    "sap",
    "sharepoint",
    "onedrive",
    "s3",
    "ec2",
    "rds",
    "ecs",
    "eks",
    "cloudfront",
    "lambda",
    "batch",
    "athena",
    "redshift",
]

APP_MODIFIERS = [
    "admin",
    "user",
    "mgr",
    "ops",
    "dev",
    "qa",
    "read",
    "write",
    "exec",
    "svc",
    "backup",
    "monitor",
    "support",
    "test",
    "prod",
]


JOINERS = ["-", "_"]


def gen_random_app_groups(num_groups: int) -> list[str]:
    """Generate a number of random {APP_PREFIX}{JOINER}{APP_MODIFIERS} groups.

    Args:
    ----
        num_groups (int): Number of groups to generate.

    Returns:
    -------
        list[str]: List of unique groups.

    Raises:
    ------
        ValueError: If num_groups is less than 0 or more combos requested than uniquely possible.

    """
    if num_groups < 0:
        msg = "Number of groups requested less than 0."
        raise ValueError(msg)

    max_combos = len(APP_PREFIXES) * len(APP_MODIFIERS)
    if num_groups > max_combos:
        msg = f"With the current app group word banks there are a maximum of {max_combos} unique combinations. Ensure num_groups <= {max_combos}"
        raise ValueError(msg)

    groups: set[str] = set()

    while len(groups) < num_groups:
        joiner = random.choice(JOINERS)  # noqa: S311 (Not crypto)
        app_prefix = random.choice(APP_PREFIXES)  # noqa: S311 (Not crypto)
        app_modifier = random.choice(APP_MODIFIERS)  # noqa: S311 (Not crypto)

        groups.add(f"{app_prefix}{joiner}{app_modifier}")

    return list(groups)


def gen_random_dept_groups(num_groups: int, num_depts: int) -> list[str]:
    """Generate a number of department groups.

    For each department included, one unmodified department group will be returned
    in the list of randomly generated groups. For example, if num_groups=3 and
    num_depts=1 and 'hr' is randomly selected as the department, then 'hr' and
    two modified hr groups will be added. (Ex: ['hr', 'hr-admin', 'hr_users'])

    **Example:**
        * *Department Groups:* hr, finance, etc...
        * *Modified Department Groups:* hr_admin, hr-lead, finance-user, etc...

    Args:
    ----
        num_groups (int): Number of groups to generate.
        num_depts (int): Number of departments to use when generating groups.

    Returns:
        list[str]: List of groups.

    Raises:
    ------
        ValueError: When {num_groups} < 0, {num_depts} < 1, or requesting more groups
        than possible to uniquely generate (Based on word bank lengths).

    """
    if num_groups < 0:
        msg = "Number of groups should be greater than 0"
        raise ValueError(msg)

    if num_depts < 1:
        msg = "Number of departments should be at least 1"
        raise ValueError(msg)

    if num_depts > len(DEPT_GROUPS):
        msg = f"Department group word bank currently has {len(DEPT_GROUPS)}. Ensure num_depts <= {len(DEPT_GROUPS)}"
        raise ValueError(msg)

    if num_depts > num_groups:
        msg = "Too many departments! Ensure num_groups >= num_depts"
        raise ValueError(msg)

    max_combos = len(DEPT_GROUPS) * len(DEPT_GROUP_MODIFIERS)
    if num_groups > max_combos:
        msg = f"With the current department word banks there are a maximum of {max_combos} unique combinations. Ensure num_groups <= {max_combos}"
        raise ValueError(msg)

    groups: set[str] = set()
    departments = random.sample(DEPT_GROUPS, k=num_depts)  # Select k unique departments
    num_dept_mod_groups = num_groups - num_depts
    dept_mod_group_partitions = random_whole_divide(num_dept_mod_groups, num_depts)

    for dept, num_mod_groups in zip(
        departments, dept_mod_group_partitions, strict=True
    ):
        groups.add(dept)  # Add unmodified department group
        orig_groups_len = len(groups)

        while len(groups) < (num_mod_groups + orig_groups_len):
            joiner = random.choice(JOINERS)  # noqa: S311 (Not crypto)
            dept_group_mod = random.choice(DEPT_GROUP_MODIFIERS)  # noqa: S311

            groups.add(f"{dept}{joiner}{dept_group_mod}")

    return list(groups)


def run() -> None:  # pragma: no cover
    """Run the custom Ansible module."""
    module = AnsibleModule(
        argument_spec=dict(
            num_groups=dict(type="int", required=True),
            group_type=dict(type="str", choices=["app", "department"], required=True),
            num_departments=dict(type="int", required=False),
        )
    )

    # Ansible args typed
    num_groups: int = module.params["num_groups"]
    group_type: str = module.params["group_type"]
    num_departments: int | None = module.params["num_departments"]

    groups: list[str] = []
    if group_type == "app":
        groups.extend(gen_random_app_groups(num_groups))
    elif group_type == "department":
        if not num_departments:
            module.fail_json(
                msg="Must specify num_departments when requesting 'department' group names"
            )

        assert num_departments is not None  # noqa: S101 (For mypy)
        groups.extend(gen_random_dept_groups(num_groups, num_departments))
    else:
        module.fail_json(msg=f"Invalid group_type: {group_type} provided")

    result = {
        "changed": False,
        "msg": f"Generated {len(groups)} groups",
        "groups": groups,
    }

    module.exit_json(**result)


if __name__ == "__main__":  # pragma: no cover
    run()
