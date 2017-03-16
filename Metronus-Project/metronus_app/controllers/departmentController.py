from django.shortcuts import render
from metronus_app.forms.departmentForm import DepartmentForm
from metronus_app.model.department import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.employee import Employee
from metronus_app.model.actor import Actor
from metronus_app.model.task import Task
from metronus_app.model.administrator import Administrator
from populate_database import basicLoad
from django.shortcuts                            import render_to_response, get_object_or_404
from metronus_app.common_utils                   import get_current_admin_or_403,get_current_employee_or_403
from django.http import HttpResponseRedirect
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth import authenticate,login
from django.http import JsonResponse

def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)
    repeated_name=False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            dname=form.cleaned_data['name']
            dep=findName(dname,admin)
            if dep is not None:
                if not dep.active:
                    dep.active=True
                    dep.save()
                    return HttpResponseRedirect('/department/view/'+str(dep.id)+"/")
                else:
                    repeated_name=True
            else:
                department=createDepartment(form,admin)
                return HttpResponseRedirect('/department/view/'+str(department.id)+"/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DepartmentForm(initial={"department_id":0,"name":""})


    return render(request, 'department_form.html', {'form': form,'repeated_name':repeated_name})

def createAsync(request):
    """
    parameters:
    form: el formulario con los datos del departamento

    returns:
    data: JSON con un mensaje de respuesta. Es un dict que contiene lo siguiente
    repeated_name: true si se ha repetido el nombre
    success:true si hubo exito, false si no

    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)

    data = {
        'repeated_name': False,
        'success':True
    }

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            dname=form.cleaned_data['name']
            dep=findName(dname,admin)
            if dep is not None:
                if not dep.active:
                    dep.active=True
                    dep.save()
                    return JsonResponse(data)
                else:
                    data['repeated_name']=True
            else:
                department=createDepartment(form,admin)
                return JsonResponse(data)

    # if a GET (or any other method) we'll create a blank form
    else:
        return HttpResponseRedirect('/department/create')

    data['success']=False
    return JsonResponse(data)


def list(request):

    """
    returns:
    departments: lista de departamentos de la compañía logeada

    template:
    department_list.html
    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)

    lista=Department.objects.filter(company_id=admin.company_id,active=True)
    return render(request, "department_list.html", {"departments": lista})
def list_for_employees(request):
    """
    OJO: esta no debería ser necesaria
    returns:
    departments: lista de departamentos del empleado logeada

    template:
    department_list.html
    """

    # Check that the current user is an employee
    employee = get_current_employee_or_403(request)

    lista=Department.objects.filter(company_id=employee.company_id,active=True,
        projectdepartment__projectdepartmentemployeerole__employee_id=employee).distinct()
    return render(request, "department_list.html", {"departments": lista})

def view(request,department_id):
    """
    url = department/view/(department_id)/

    parameters:
    department_id: id del department

    returns:
    department: datos del departamento
    employees: objetos Empleados
    tasks: lista de tareas del departamento

    template: department_view.html
    """
    department = get_object_or_404(Department, pk=department_id)
    checkRoleForList(department,request)

    tasks=Task.objects.filter(active=True, projectDepartment_id__department_id__id=department_id)

    employees = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__department_id=department)

    return render(request, 'department_view.html', {'department': department, 'employees': employees,'tasks':tasks})

def edit(request,department_id):
    """
    url = department/edit/(department_id)/

    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)
    repeated_name=False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            department=get_object_or_404(Department,pk=form.cleaned_data['department_id'])
            if checkCompanyDepartment(department,admin.company_id):
                dep=findName(form.cleaned_data['name'],admin)
                #dep does not exists or it's the same
                if dep is None or dep.id==department.id:
                    editDepartment(department,form)
                    return HttpResponseRedirect('/department/view/'+str(department.id)+"/")
                else:
                    if dep.active:
                        repeated_name=True
    # if a GET (or any other method) we'll create a blank form
    else:

        department=get_object_or_404(Department,pk=department_id)
        form = DepartmentForm(initial={"name":department.name,"department_id":department.id})


    return render(request, 'department_form.html', {'form': form,'repeated_name':repeated_name})

def delete(request,department_id):
    """
    url = department/delete/(department_id)/
    parameters:
    department_id: the department id to delete

    returns:
    nothing

    template:
    deparment_list.html
    """


    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)

    department=get_object_or_404(Department,pk=department_id)
    if checkCompanyDepartment(department,admin.company_id):
        deleteDepartment(department)

    return HttpResponseRedirect('/department/list')

#Auxiliar methods, containing the operation logic
def findName(dname,admin):
    return Department.objects.filter(name=dname,company_id=admin.company_id).first()

def createDepartment(form,admin):

    dname=form.cleaned_data['name']
    company=admin.company_id
    return Department.objects.create(name=dname,active=True,company_id=company)

def editDepartment(department,form):

    department.name = form.cleaned_data['name']
    department.save()

def deleteDepartment(department):
    department.active=False
    department.save()

def checkCompanyDepartmentSession(department,admin):
    """
    checks if the department belongs to the logged company
    """
    return checkCompanyDepartment(department,admin.company_id)

def checkCompanyDepartment(department,company_id):
    """
    checks if the department belongs to the specified company
    """
    res= department is not None and company_id==department.company_id and department.active
    if not res:
        raise PermissionDenied
    return res



def checkRoleForList(dep,request):

    actor=None
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

    # Check that the admin has permission to view that employee
    if dep.company_id != actor.company_id:
        raise PermissionDenied
    
    if actor.user_type!='A':
        isAdminOrTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name__in=["Administrator" , "Team manager"])
        res=isAdminOrTeamManager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                        projectDepartment_id__department_id=dep)
            res=roles.count()>0
        if not res:
            raise PermissionDenied
