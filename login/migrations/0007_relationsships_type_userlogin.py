# Generated by Django 3.1.1 on 2020-10-02 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0006_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('TypeId', models.IntegerField(primary_key=True, serialize=False)),
                ('Description', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UserId', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='login.user')),
            ],
        ),
        migrations.CreateModel(
            name='Relationsships',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TypeId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.type')),
                ('UserA', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserA', to='login.user')),
                ('UserB', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserB', to='login.user')),
            ],
        ),
    ]
