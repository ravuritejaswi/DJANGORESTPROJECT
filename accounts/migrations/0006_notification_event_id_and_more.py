import uuid
from django.db import migrations, models


def populate_event_ids(apps, schema_editor):
    Notification = apps.get_model("accounts", "Notification")

    for notification in Notification.objects.filter(event_id__isnull=True):
        notification.event_id = str(uuid.uuid4())
        notification.save(update_fields=["event_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="event_id",
            field=models.CharField(
                max_length=255,
                null=True,
                editable=False,
            ),
        ),

        migrations.RunPython(
            populate_event_ids,
            migrations.RunPython.noop,
        ),

        migrations.AlterField(
            model_name="notification",
            name="event_id",
            field=models.CharField(
                max_length=255,
                default=uuid.uuid4,
                editable=False,
            ),
        ),

        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                fields=("user", "event_id"),
                name="unique_user_event_notification",
            ),
        ),
    ]