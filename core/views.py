from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DirectorySearchForm, EmployeeForm, LeaveRequestForm
from .models import Attendance, Department, Employee, LeaveRequest


def user_in_groups(user, group_names):
    return user.is_superuser or user.groups.filter(name__in=group_names).exists()


def is_admin(user):
    return user_in_groups(user, ['Admin'])


def is_manager(user):
    return user_in_groups(user, ['Admin', 'Manager'])


@login_required
def dashboard(request):
    total_employees = Employee.objects.count()
    departments = Department.objects.annotate(count=Count('employees')).order_by('-count')[:5]
    today = date.today()
    present_today = Attendance.objects.filter(date=today, status='present').count()
    pending_leaves = LeaveRequest.objects.filter(status=LeaveRequest.PENDING).count()

    context = {
        'total_employees': total_employees,
        'departments': departments,
        'present_today': present_today,
        'pending_leaves': pending_leaves,
        'is_admin': is_admin(request.user),
        'is_manager': is_manager(request.user),
    }
    return render(request, 'dashboard.html', context)


@login_required
def employee_list(request):
    form = DirectorySearchForm(request.GET or None)
    qs = Employee.objects.select_related('user', 'department').all()
    if form.is_valid():
        q = form.cleaned_data.get('q')
        dept = form.cleaned_data.get('department')
        if q:
            qs = qs.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(user__username__icontains=q) | Q(title__icontains=q))
        if dept:
            qs = qs.filter(department=dept)
    qs = qs.order_by('user__first_name', 'user__last_name')
    return render(request, 'employees/list.html', {'employees': qs, 'form': form, 'is_manager': is_manager(request.user)})


@login_required
@user_passes_test(is_manager)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            # For simplicity, create a User with username/email fields if provided
            username = request.POST.get('username') or request.POST.get('email')
            if not username:
                messages.error(request, 'Username or email required.')
            else:
                user = User.objects.create_user(username=username, email=request.POST.get('email') or '', password='ChangeMe123!')
                user.first_name = form.cleaned_data.get('first_name') or ''
                user.last_name = form.cleaned_data.get('last_name') or ''
                user.save()
                employee = form.save(commit=False)
                employee.user = user
                employee.save()
                messages.success(request, 'Employee created.')
                return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/create.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated.')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/edit.html', {'form': form, 'employee': employee})


@login_required
def attendance_list(request):
    # Show own records for employees; managers/admin see all
    if is_manager(request.user):
        records = Attendance.objects.select_related('employee__user', 'employee__department').order_by('-date')[:200]
    else:
        employee = getattr(request.user, 'employee_profile', None)
        if not employee:
            # Auto-create a minimal employee profile to avoid empty state after first check-in
            from .models import Employee
            employee = Employee.objects.create(user=request.user)
        records = Attendance.objects.filter(employee=employee).order_by('-date')
    return render(request, 'attendance/list.html', {'records': records, 'is_manager': is_manager(request.user)})


@login_required
def attendance_checkin(request):
    # Ensure the user has an employee profile
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        from .models import Employee
        employee, _ = Employee.objects.get_or_create(user=request.user)
    from django.utils import timezone as djtz
    today = date.today()
    att, _ = Attendance.objects.get_or_create(employee=employee, date=today, defaults={'status': 'present'})
    if att.check_in:
        messages.info(request, f"Already checked in at {att.check_in.strftime('%H:%M')}.")
    else:
        att.check_in = djtz.now()
        att.status = 'present'
        att.save()
        messages.success(request, 'Checked in successfully.')
    return redirect('attendance_list')


@login_required
@user_passes_test(is_manager)
def attendance_mark(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    status = request.GET.get('status', 'present')
    Attendance.objects.update_or_create(employee=employee, date=date.today(), defaults={'status': status})
    messages.success(request, f"Attendance marked {status} for {employee}.")
    return redirect('attendance_list')


@login_required
def leave_list(request):
    if is_manager(request.user):
        leaves = LeaveRequest.objects.select_related('employee__user').all()
    else:
        employee = getattr(request.user, 'employee_profile', None)
        if not employee:
            leaves = LeaveRequest.objects.none()
        else:
            leaves = LeaveRequest.objects.filter(employee=employee)
    return render(request, 'leaves/list.html', {'leaves': leaves, 'is_manager': is_manager(request.user)})


@login_required
def leave_request_create(request):
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        return HttpResponseForbidden('Only employees can request leave')
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.save()
            messages.success(request, 'Leave request submitted.')
            return redirect('leave_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'leaves/create.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def leave_approve(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = LeaveRequest.APPROVED
    leave.save()
    messages.success(request, 'Leave approved.')
    return redirect('leave_list')


@login_required
@user_passes_test(is_manager)
def leave_reject(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = LeaveRequest.REJECTED
    leave.save()
    messages.success(request, 'Leave rejected.')
    return redirect('leave_list')
