# Generated by Django 5.1.1 on 2024-11-21 04:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_alter_observaciones_tareas_obsevaciones_cambiada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipos_desarrollo',
            name='tarea_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.tareas'),
        ),
    ]
