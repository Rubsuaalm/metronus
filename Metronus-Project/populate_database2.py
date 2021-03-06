from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.model.administrator import Administrator
from metronus_app.model.task import Task
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.goalEvolution import GoalEvolution
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.db import transaction
from datetime import timedelta
from django.utils import timezone
import string
import random


def ranstr():
    """ Returns a 8-character random string"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


# Métodos para crear objetos
def create_departments(company):
    """
    Creates a random department for a given company
    """
    Department.objects.create(
        name="department"+ranstr(),
        active=True,
        company_id=company
    )


def create_projects(company):
    """
    Creates a random project for a given company
    """
    Project.objects.create(name="project"+ranstr(), deleted=False, company_id=company)


def create_employee_in_projdept(project, department, company):
    """
    creates an employee and assigns him/her a new role
    """
    user = User.objects.create_user(
        username="employee"+ranstr(),
        password="metronus",
        email=ranstr() + "@metronus.es",
        first_name=ranstr(),
        last_name=ranstr()
    )

    employee = Employee.objects.create(
        user=user,
        user_type="E",
        identifier=ranstr(),
        phone="123123123",
        company_id=company,
        price_per_hour=random.uniform(4, 16)
    )

    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

    role = Role.objects.get(tier=random.choice([10, 15, 20, 40, 50]))
    ProjectDepartmentEmployeeRole.objects.create(projectDepartment_id=pd, role_id=role, employee_id=employee)

    return employee


def create_task_in_projdept(project, department, admin, r_date):
    """
    creates a task for a given project and department, either with production goal or not
    """
    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)
    measure = random.choice([True, True, True, False])  # Make task have a 25% chance of not having a production goal

    if measure:
        pgoal = random.uniform(50, 100)
        pdescription = random.choice(["kgs", "fresas", "granos de harina", "estrellitas", "cms"])
        pprice_units = random.uniform(0.02, 2)
        pprice_hours = None
    else:
        pgoal = None
        pdescription = ""
        pprice_units = None
        pprice_hours = random.uniform(4, 20)

    task = Task.objects.create(
        name="task"+ranstr(),
        description=ranstr(),
        actor_id=admin,
        production_goal=pgoal,
        goal_description=pdescription,
        projectDepartment_id=pd,
        price_per_hour=pprice_hours,
        price_per_unit=pprice_units
    )
    Task.objects.filter(pk=task.id).update(registryDate=r_date.strftime('%Y-%m-%d')+" 10:00+00:00")

    # Generate random number of previous goals
    for _ in range(random.randint(3, 7)):
        create_goal_evolution(task, admin, r_date, measure)
    return task.id


def create_goal_evolution(task, actor, r_date, measure):
    """
    creates a production goal registry for a task in the past
    rDate is the task registryDate, so we will create a date before that
    measure is true if there was a production goal, otherwise the task was paid per hour
    """
    if measure:
        pgoal = random.uniform(40, 100)
        pprice_units = random.uniform(0.02, 2)
        pprice_hours = None
    else:
        pgoal = None
        pprice_units = None
        pprice_hours = random.uniform(4, 20)

    ge1 = GoalEvolution.objects.create(
        task_id=task,
        actor_id=actor,
        production_goal=pgoal,
        goal_description=task.goal_description,
        price_per_hour=pprice_hours,
        price_per_unit=pprice_units
        )
    # get a date before the last task update
    date = r_date - timedelta(days=random.randint(2, 30))

    GoalEvolution.objects.filter(pk=ge1.id).update(registryDate=date.strftime('%Y-%m-%d')+" 10:00+00:00")


def create_timelog_in_task(task, duration, date, employee):
    """
    creates a timelog for an employee involving a task during a specific date
    """

    # Check that there isn't a timelog for the same employee, task and day
    if TimeLog.objects.filter(
        workDate__year=date.year,
        workDate__month=date.month,
        workDate__day=date.day,
        task_id=task,
        employee_id=employee
    ).exists():
        return

    if task.production_goal is not None and task.production_goal != "":
        punits = random.uniform(0.5, 1.5)*duration/60*task.production_goal
    else:
        punits = None
    TimeLog.objects.create(
        description=ranstr(),
        workDate=date,
        duration=duration,
        task_id=task,
        produced_units=punits,
        employee_id=employee
    )


# ################################# Party hard a partir de aquí ##################################
@transaction.atomic
def random_load():
    """
    loads a lot of random data
    """
    populate_roles()
    # create company
    company = Company.objects.create(cif="A00000002", company_name="metronus", short_name="metronus",
                                     email="info@metronus.es", phone="123456789")
    # From company:metronus: admin
    adminuser = User.objects.create_user(
        username="metronus",
        password="metronus",
        email="admin2@gmail.com",
        first_name="admin2",
        last_name="admin2")

    admin = Administrator.objects.create(
        user=adminuser,
        user_type="A",
        identifier="12345",
        phone="123456789",
        company_id=company)
    # create departments
    for _ in range(random.randint(5, 8)):
        create_departments(company)
    # create projects
    for _ in range(random.randint(5, 7)):
        create_projects(company)

    # get projects and departments
    departments = list(Department.objects.filter(company_id=company, active=True))
    projects = list(Project.objects.filter(company_id=company, deleted=False))

    # Get all dates between in a month
    dates = []
    d1 = timezone.now()

    for i in range(30):
        dates.append(d1 - timedelta(days=i))

    for dpmt in departments:
        for project in projects:
            # Create between 2 and 7 employees for each department and project
            for _ in range(random.randint(2, 7)):
                create_employee_in_projdept(project, dpmt, company)
            # Create between 2 and 4 tasks for each department
            for _ in range(random.randint(2, 4)):
                task_id = create_task_in_projdept(project, dpmt, admin, random.choice(dates))
                task = Task.objects.get(pk=task_id)
                employees = list(Employee.objects.filter(
                    projectdepartmentemployeerole__projectDepartment_id__project_id=project,
                    projectdepartmentemployeerole__projectDepartment_id__department_id=dpmt))
                # Create between 10 and 25 timelogs for each task and employee
                for employee in employees:
                    for _ in range(random.randint(10, 25)):
                        duration = random.randint(40, 480)

                        date = random.choice(dates)
                        create_timelog_in_task(task, duration, date, employee)


def populate_roles():
    """
    Loads... the available roles!!
    """
    # El gerente
    Role.objects.create(name="EXECUTIVE", tier=50)
    # El jefe de proyecto
    Role.objects.create(name="PROJECT_MANAGER", tier=40)
    # El coordinador del departamento
    Role.objects.create(name="COORDINATOR", tier=20)
    # El jefe de equipo
    Role.objects.create(name="TEAM_MANAGER", tier=15)
    # El empleado
    Role.objects.create(name="EMPLOYEE", tier=10)
