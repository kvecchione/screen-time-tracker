from django.db import migrations


def forwards(apps, schema_editor):
    DailyTracking = apps.get_model('tracker', 'DailyTracking')
    DailyTracking.objects.filter(status='pending').update(status='not_earned')


def backwards(apps, schema_editor):
    DailyTracking = apps.get_model('tracker', 'DailyTracking')
    # Revert only rows that were converted (best-effort: convert all 'not_earned' back to 'pending')
    DailyTracking.objects.filter(status='not_earned').update(status='pending')


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_update_status_default'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
