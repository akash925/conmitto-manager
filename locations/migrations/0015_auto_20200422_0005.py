# Generated by Django 3.0.3 on 2020-04-22 00:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0029_auto_20200422_0005'),
        ('locations', '0014_auto_20200327_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
        migrations.AlterField(
            model_name='facility',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
        migrations.AlterField(
            model_name='locationinstance',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
        migrations.AlterField(
            model_name='region',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
        migrations.AlterField(
            model_name='subzone',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
        migrations.AlterField(
            model_name='wing',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
        migrations.AlterField(
            model_name='zone',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.Personnel'),
        ),
    ]
