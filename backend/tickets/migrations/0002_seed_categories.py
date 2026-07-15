from django.db import migrations

DEFAULT_CATEGORIES = ["Bug", "Feature Request", "Access Request", "Other"]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("tickets", "Category")
    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model("tickets", "Category")
    Category.objects.filter(name__in=DEFAULT_CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
