from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailytracking',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[('earned', 'Earned'), ('not_earned', 'Not Earned')],
                default='not_earned',
            ),
        ),
    ]
