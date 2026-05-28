from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0019_delete_activitylog"),
    ]

    operations = [
        migrations.DeleteModel(
            name="VisitorEvent",
        ),
    ]
