# Generated by Django 4.2.7 on 2023-11-29 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0007_loan_is_fully_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='loan_status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Rejected'), (3, 'Paid'), (4, 'Partially Paid')], default=0),
        ),
    ]
