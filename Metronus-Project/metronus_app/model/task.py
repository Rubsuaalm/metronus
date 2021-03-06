from django.db import models
from metronus_app.model.actor import Actor
from metronus_app.model.projectDepartment import ProjectDepartment


class Task(models.Model):
    """ Esto es una clase del modelo. Totalmente inesperado"""

    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    registryDate = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    actor_id = models.ForeignKey(Actor)
    projectDepartment_id = models.ForeignKey(ProjectDepartment)

    production_goal = models.FloatField(null=True, blank=True)
    goal_description = models.CharField(blank=True, max_length=100, default="")

    price_per_unit = models.FloatField(null=True, blank=True)
    price_per_hour = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('projectDepartment_id', 'name')
