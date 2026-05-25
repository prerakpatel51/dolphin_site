from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_tax_settings_and_booking_tax"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="tour",
            index=models.Index(fields=["is_active", "sort_order", "name"], name="tour_active_sort_idx"),
        ),
        migrations.AddIndex(
            model_name="tourslot",
            index=models.Index(fields=["tour", "is_active", "date", "time"], name="slot_tour_act_date_idx"),
        ),
        migrations.AddIndex(
            model_name="tourslot",
            index=models.Index(fields=["is_active", "date", "time"], name="slot_act_date_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["slot", "status"], name="booking_slot_status_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["user", "-created_at"], name="booking_user_created_idx"),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["customer_email", "-created_at"], name="booking_email_created_idx"),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(fields=["tour", "is_approved", "is_featured", "-created_at"], name="review_tour_state_idx"),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(fields=["user", "tour"], name="review_user_tour_idx"),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(fields=["tour", "author_email"], name="review_tour_email_idx"),
        ),
        migrations.AddIndex(
            model_name="mailinglistentry",
            index=models.Index(fields=["subscribed", "-created_at"], name="mailing_sub_created_idx"),
        ),
        migrations.AddIndex(
            model_name="promocode",
            index=models.Index(fields=["is_active", "expires_at"], name="promo_active_exp_idx"),
        ),
        migrations.AddIndex(
            model_name="promocode",
            index=models.Index(fields=["locked_to_email"], name="promo_locked_email_idx"),
        ),
    ]
