# Generated by Django 2.2 on 2021-06-25 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apirest', '0012_auto_20210623_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boleta',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='boletadetalle',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='librodiario',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]