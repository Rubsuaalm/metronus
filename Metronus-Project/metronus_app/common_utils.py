from django.core.exceptions                      import PermissionDenied
from metronus_app.model.administrator            import Administrator
from metronus_app.model.employee            import Employee
from django.core.exceptions                      import ObjectDoesNotExist

from PIL import Image


# Image limit parameters
FILE_SIZE = 100000000
HEIGHT = 256
WIDTH = 256
VALID_FORMATS = ['JPEG', 'JPG', 'PNG']


def get_current_admin_or_403(request):
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied


def get_current_employee_or_403(request):

    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Employee.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def check_company_contains_actor(company, username):
    ret = False
    actor_set = company.actor_set.all()
    if actor_set is not None:
        for actor in actor_set:
            if str(username) == str(actor.user.username):
                ret = True
        if ret is False:
            raise PermissionDenied


def checkImage(form, param):
    """
    checks if logo has the correct dimensions and extension
    """
    logo = form.cleaned_data[param]

    if logo is not None:
        image = Image.open(logo, mode="r")
        xsize, ysize = image.size
        ext = image.format in VALID_FORMATS

        return xsize <= WIDTH and ysize <= HEIGHT and ext
    else:
        return True