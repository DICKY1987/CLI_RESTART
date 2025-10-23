import pytest

from cli_multi_rapid.security.framework import Permission, Role, User
from cli_multi_rapid.security.rbac import RoleBasedAccessControl


@pytest.fixture()
def rbac():
    return RoleBasedAccessControl()


@pytest.fixture()
def base_user():
    return User(
        id="user-123",
        username="alice",
        email="alice@example.com",
        roles={Role.GUEST},
    )


def test_assign_and_revoke_role_permissions(rbac):
    rbac.assign_permissions_to_role(Role.DEVELOPER, [Permission.WORKFLOW_WRITE])
    assert rbac.get_role_permissions(Role.DEVELOPER) == {Permission.WORKFLOW_WRITE}

    rbac.revoke_permissions_from_role(Role.DEVELOPER, [Permission.WORKFLOW_WRITE])
    assert rbac.get_role_permissions(Role.DEVELOPER) == set()


def test_direct_user_permissions_override_roles(rbac, base_user):
    rbac.assign_permissions_to_role(Role.GUEST, [Permission.WORKFLOW_READ])
    rbac.assign_permission_to_user(base_user.id, Permission.WORKFLOW_EXECUTE)

    permissions = rbac.get_user_permissions(base_user)
    assert permissions == {Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE}

    rbac.revoke_permission_from_user(base_user.id, Permission.WORKFLOW_EXECUTE)
    assert rbac.get_user_permissions(base_user) == {Permission.WORKFLOW_READ}


def test_permission_checks_across_multiple_roles(rbac):
    user = User(
        id="user-456",
        username="bob",
        email="bob@example.com",
        roles={Role.GUEST, Role.DEVELOPER},
    )
    rbac.assign_permissions_to_role(
        Role.GUEST, [Permission.WORKFLOW_READ, Permission.SYSTEM_HEALTH_VIEW]
    )
    rbac.assign_permissions_to_role(
        Role.DEVELOPER,
        [Permission.WORKFLOW_WRITE, Permission.ADAPTER_USE_AI],
    )

    assert rbac.check_permission(user, Permission.WORKFLOW_READ) is True
    assert rbac.check_any_permission(
        user,
        [Permission.WORKFLOW_EXECUTE, Permission.ADAPTER_USE_AI],
    )
    assert rbac.check_all_permissions(
        user,
        [Permission.WORKFLOW_READ, Permission.ADAPTER_USE_AI],
    )
    assert (
        rbac.check_all_permissions(
            user,
            [Permission.WORKFLOW_READ, Permission.ADAPTER_USE_AI],
        )
        is True
    )
    assert (
        rbac.check_all_permissions(
            user,
            [Permission.WORKFLOW_READ, Permission.SYSTEM_CONFIG_EDIT],
        )
        is False
    )
    assert not rbac.check_any_permission(
        user,
        [Permission.SYSTEM_CONFIG_EDIT, Permission.WORKFLOW_DELETE],
    )


def test_role_queries_and_summary(rbac, base_user):
    base_user.roles.add(Role.DEVELOPER)
    rbac.assign_permissions_to_role(
        Role.GUEST,
        [Permission.WORKFLOW_READ, Permission.SYSTEM_HEALTH_VIEW],
    )
    rbac.assign_permissions_to_role(
        Role.DEVELOPER,
        [Permission.WORKFLOW_WRITE, Permission.ADAPTER_USE_DETERMINISTIC],
    )
    rbac.assign_permission_to_user(base_user.id, Permission.ADMIN_SECURITY_AUDIT)

    assert rbac.has_role(base_user, Role.GUEST)
    assert rbac.has_any_role(base_user, [Role.ADMIN, Role.DEVELOPER])

    summary = rbac.get_effective_permissions_summary(base_user)
    assert summary["user_id"] == base_user.id
    assert summary["username"] == base_user.username
    assert set(summary["roles"]) == {Role.GUEST.value, Role.DEVELOPER.value}
    assert set(summary["direct_permissions"]) == {Permission.ADMIN_SECURITY_AUDIT.value}
    assert summary["effective_permissions"] == sorted(
        [
            Permission.WORKFLOW_READ.value,
            Permission.SYSTEM_HEALTH_VIEW.value,
            Permission.WORKFLOW_WRITE.value,
            Permission.ADAPTER_USE_DETERMINISTIC.value,
            Permission.ADMIN_SECURITY_AUDIT.value,
        ]
    )

    mapping = rbac.list_all_role_permissions()
    assert set(mapping[Role.GUEST.value]) == {
        Permission.WORKFLOW_READ.value,
        Permission.SYSTEM_HEALTH_VIEW.value,
    }
    assert set(mapping[Role.DEVELOPER.value]) == {
        Permission.WORKFLOW_WRITE.value,
        Permission.ADAPTER_USE_DETERMINISTIC.value,
    }


def test_get_permissions_for_unknown_role_returns_empty(rbac):
    assert rbac.get_permissions_for_roles({Role.ADMIN}) == set()
