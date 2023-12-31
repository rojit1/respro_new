# Generated by Django 4.0.6 on 2023-06-26 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0004_alter_bill_discount_amount_alter_bill_grand_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tablreturnentry',
            name='fiscal_year',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='tablreturnentry',
            unique_together={('bill_no', 'fiscal_year')},
        ),
    ]
