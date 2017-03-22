# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-16 12:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('A', 'Administrator'), ('E', 'Employee')], default='E', max_length=1)),
                ('identifier', models.CharField(max_length=15)),
                ('phone', models.CharField(max_length=15)),
                ('registryDate', models.DateTimeField(auto_now=True)),
                ('picture', models.ImageField(blank=True, default='/static/avatar.png', null=True, upload_to='actor')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cif', models.CharField(max_length=9, unique=True)),
                ('company_name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=50, unique=True)),
                ('visible_short_name', models.BooleanField(default=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
                ('registryDate', models.DateTimeField(auto_now=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cif', models.CharField(max_length=9, unique=True)),
                ('company_name', models.CharField(max_length=100)),
                ('registryDate', models.DateTimeField()),
                ('endDate', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('registryDate', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Company')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('A', 'Alta'), ('B', 'Baja')], default='A', max_length=1)),
                ('event_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('registryDate', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Company')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Department')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectDepartmentEmployeeRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roleDate', models.DateTimeField(auto_now=True)),
                ('projectDepartment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.ProjectDepartment')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=200)),
                ('registryDate', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('registryDate', models.DateTimeField(auto_now=True)),
                ('workDate', models.DateTimeField()),
                ('duration', models.PositiveSmallIntegerField(default=1)),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Task')),
            ],
        ),
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('actor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='metronus_app.Actor')),
            ],
            bases=('metronus_app.actor',),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('actor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='metronus_app.Actor')),
            ],
            bases=('metronus_app.actor',),
        ),
        migrations.AddField(
            model_name='task',
            name='actor_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Actor'),
        ),
        migrations.AddField(
            model_name='task',
            name='projectDepartment_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.ProjectDepartment'),
        ),
        migrations.AddField(
            model_name='projectdepartmentemployeerole',
            name='role_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Role'),
        ),
        migrations.AddField(
            model_name='actor',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Company'),
        ),
        migrations.AddField(
            model_name='actor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='timelog',
            name='employee_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Employee'),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('projectDepartment_id', 'name')]),
        ),
        migrations.AddField(
            model_name='projectdepartmentemployeerole',
            name='employee_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Employee'),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('name', 'company_id')]),
        ),
        migrations.AddField(
            model_name='employeelog',
            name='employee_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metronus_app.Employee'),
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=set([('name', 'company_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectdepartmentemployeerole',
            unique_together=set([('projectDepartment_id', 'employee_id', 'role_id')]),
        ),
    ]
