from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_user_accepts_marketing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="tagline",
            field=models.CharField(
                default="Small-group dolphin, wildlife, sunset, and rocket-launch boat tours on Florida's Space Coast.",
                max_length=240,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="seo_title",
            field=models.CharField(
                default="Dolphin Island Tours | Merritt Island Dolphin & Sunset Boat Tours",
                max_length=70,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="seo_description",
            field=models.CharField(
                default="Book small-group dolphin, manatee, wildlife, sunset, and rocket launch boat tours from Merritt Island near Cocoa Beach and Cape Canaveral.",
                max_length=180,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="seo_keywords",
            field=models.CharField(
                default="Merritt Island dolphin tours, Cocoa Beach dolphin tour, Cape Canaveral boat tour, Space Coast wildlife tour, Indian River Lagoon tour, Florida sunset cruise",
                max_length=240,
            ),
        ),
    ]
