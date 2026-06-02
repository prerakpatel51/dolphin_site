from django.db import migrations, models


FAQS = [
    (
        "What wildlife can we see on a Merritt Island boat tour?",
        "Guests often see bottlenose dolphins, manatees, pelicans, ospreys, shorebirds, and other Indian River Lagoon wildlife. Wildlife sightings vary by season and conditions.",
    ),
    (
        "Where do Dolphin Island Tours depart from?",
        "Tours depart from 2700 Harbor Town Drive in Merritt Island, Florida, near Cocoa Beach, Cape Canaveral, and Port Canaveral.",
    ),
    (
        "Do you offer sunset cruises near Cocoa Beach?",
        "Yes. Dolphin Island Tours offers small-group sunset cruises on the Indian River Lagoon from Merritt Island.",
    ),
    (
        "Can we watch a rocket launch from the boat?",
        "Launch-day departures may be available when schedules and conditions line up. Contact Dolphin Island Tours before booking if rocket launch viewing is your main goal.",
    ),
    (
        "How many guests are on each tour?",
        "Tours are small-group experiences for 3 to 6 guests per boat.",
    ),
    (
        "What should I bring?",
        "Sunscreen, hat, sunglasses, water, a light layer, and your camera. Closed-toe shoes recommended.",
    ),
    (
        "What if the weather is bad?",
        "If we have to cancel for weather we'll reschedule or refund in full - no questions.",
    ),
    (
        "Are kids welcome?",
        "Absolutely. Life jackets in all sizes provided. Best for ages 4+.",
    ),
    (
        "Can we charter privately?",
        "Yes - the boat is yours for 3-6 guests on every tour. No strangers.",
    ),
    (
        "Where do we meet?",
        "2700 Harbor Town Drive, Merritt Island, FL 32952. Arrive 15 minutes before departure.",
    ),
]


def seed_faqs(apps, schema_editor):
    FAQItem = apps.get_model("api", "FAQItem")
    for index, (question, answer) in enumerate(FAQS, start=1):
        FAQItem.objects.get_or_create(
            question=question,
            defaults={
                "answer": answer,
                "sort_order": index * 10,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0027_footer_and_marketing_copy"),
    ]

    operations = [
        migrations.CreateModel(
            name="FAQItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.CharField(max_length=220)),
                ("answer", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "FAQ item",
                "verbose_name_plural": "FAQ items",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="faqitem",
            index=models.Index(fields=["is_active", "sort_order"], name="faq_active_sort_idx"),
        ),
        migrations.RunPython(seed_faqs, migrations.RunPython.noop),
    ]
