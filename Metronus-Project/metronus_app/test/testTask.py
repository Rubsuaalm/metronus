from metronus_app.model.department import Department
from metronus_app.model.company import Company
from metronus_app.controllers.departmentController import *
from django.contrib.auth.models                  import User
from django.test import TestCase, Client
from metronus_app.model.employee         import Employee
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from populate_database import populate_database
class TaskTestCase(TestCase):
    def setUp(self):
        populate_database()

    def test_create_task_positive(self):
        # Logged in as an administrator, try to create a task
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = Task.objects.all().count()

        response = c.post("/task/create", {
            "task_id": "0",
            "name": "dep4",
        })

        self.assertEquals(response.status_code, 302)

        # Check that the task has been successfully created

        dep = Task.objects.all().last()
        self.assertEquals(dep.name, "dep4")
        self.assertEquals(dep.active,True)
        logs_after = Task.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_task_duplicate(self):
        # Logged in as an administrator, try to create an task with the name of an existing company
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = Task.objects.all().count()

        response = c.post("/task/create", {
            "task_id": "0",
            "name": "dep1",
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["repeated_name"],True)


    def test_create_task_not_logged(self):
        c = Client()
        response = c.get("/task/create")
        self.assertEquals(response.status_code, 403)

    def test_create_task_not_allowed(self):
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/task/create")
        self.assertEquals(response.status_code, 403)


    def test_list_tasks_positive(self):
        c = Client()
        c.login(username="ddlsb", password="123456")

        department=Department.objects.filter(name="Backend").first()
        response = c.get("/task/list_department?department_id="+str(department.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["tasks"]), 2)
        self.assertEquals(response.context["tasks"][0].name, "Hacer cosas")

    def test_list_tasks_not_logged(self):
        c = Client()
        department=Department.objects.filter(name="Backend").first()
        response = c.get("/task/list_department?department_id="+str(department.id))
        self.assertEquals(response.status_code, 403)

    def test_list_tasks_not_allowed(self):
        c = Client()
        c.login(username="anddonram", password="123456")
        department=Department.objects.filter(name="Frontend").first()
        response = c.get("/task/list_department?department_id="+str(department.id))
        self.assertEquals(response.status_code, 403)


    def test_edit_task_get(self):
        c = Client()
        c.login(username="agubelu", password="123456")
        department=Department.objects.filter(name="Backend").first()
        response = c.get("/task//list_department?department_id="+str(department.id))
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/edit?task_id="+str(dep_id))
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["name"], "dep1")
        self.assertEquals(form.initial["task_id"], dep_id)

    def test_edit_task_404(self):
        c = Client()
        c.login(username="anddonram", password="123456")

        response = c.get("/task/edit?task_id=9000")
        self.assertEquals(response.status_code, 404)


    def test_delete_task_positive(self):
        c = Client()
        c.login(username="agubelu", password="123456")
        department=Department.objects.filter(name="Backend").first()
        response = c.get("/task/list_department?department_id="+str(department.id))
        dep_id=response.context["tasks"][0].id

        response = c.get("/task/delete?task_id="+str(dep_id))
        self.assertRedirects(response, "/task/list", fetch_redirect_response=False)

        self.assertFalse(Task.objects.get(pk=dep_id).active)

    def test_delete_task_not_allowed(self):
        c = Client()
        c.login(username="andjimrio", password="123456")
        department=Department.objects.filter(name="Backend").first()
        response = c.get("/task/list_department?department_id="+str(department.id))
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/delete?task_id="+str(dep_id))
        self.assertEquals(response.status_code, 403)

    def test_delete_task_not_active(self):
        c = Client()
        c.login(username="ddlsb", password="123456")

        dep_id=Task.objects.get(active=False).id
        response = c.get("/task/delete?task_id="+str(dep_id))
        self.assertEquals(response.status_code, 403)
