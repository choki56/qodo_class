from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Employee, Department, Attendance, LeaveRequest

class Command(BaseCommand):
    help = 'Create default roles and assign basic permissions'

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        employee_group, _ = Group.objects.get_or_create(name='Employee')

        # Basic permissions: Managers can change Employee, approve leaves (change LeaveRequest)
        ct_employee = ContentType.objects.get_for_model(Employee)
        ct_leave = ContentType.objects.get_for_model(LeaveRequest)

        perms = Permission.objects.filter(content_type__in=[ct_employee, ct_leave])
        manager_group.permissions.set(perms)
        admin_group.permissions.set(Permission.objects.all())
        employee_group.permissions.clear()

        self.stdout.write(self.style.SUCCESS('Roles bootstrapped: Admin, Manager, Employee'))
