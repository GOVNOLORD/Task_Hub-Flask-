from flask_principal import Permission, RoleNeed

admin_permission = Permission(RoleNeed('admin'))
project_manager_permission = Permission(RoleNeed('project_manager'))
project_member_permission = Permission(RoleNeed('project_member'))

