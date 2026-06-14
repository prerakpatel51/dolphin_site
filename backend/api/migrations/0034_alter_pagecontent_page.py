from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0033_guest_lookup_and_long_page_keywords"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagecontent",
            name="page",
            field=models.CharField(
                choices=[
                    ("home", "Home"),
                    ("tours", "Tours listing"),
                    ("book", "Booking"),
                    ("reviews", "Reviews"),
                    ("about", "About"),
                    ("contact", "Contact"),
                    ("find_booking", "Find booking"),
                    ("login", "Login"),
                    ("signup", "Sign up"),
                    ("account", "Account"),
                    ("bookings", "My bookings"),
                    ("forgot_password", "Forgot password"),
                    ("reset_password", "Reset password"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
    ]
