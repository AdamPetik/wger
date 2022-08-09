# Generated by Django 3.2.14 on 2022-08-09 12:33

from django.db import migrations, models
import django.db.models.deletion
import uuid
import wger.nutrition.models.image
import wger.utils.helpers


def generate_uuids(apps, schema_editor):
    """
    Generate new UUIDs for each exercise
    :param apps:
    :param schema_editor:
    :return:
    """
    Ingredient = apps.get_model("nutrition", "Ingredient")
    for ingredient in Ingredient.objects.all():
        ingredient.uuid = uuid.uuid4()
        ingredient.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20210726_1729'),
        ('nutrition', '0011_alter_logitem_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID'),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    )
                ),
                (
                    'license_author',
                    models.CharField(
                        blank=True,
                        help_text=
                        'If you are not the author, enter the name or source here. This is needed for some licenses e.g. the CC-BY-SA.',
                        max_length=50,
                        null=True,
                        verbose_name='Author'
                    )
                ),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')),
                (
                    'image',
                    models.ImageField(
                        help_text='Only PNG and JPEG formats are supported',
                        upload_to=wger.nutrition.models.image.ingredient_image_upload_dir,
                        verbose_name='Image'
                    )
                ),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('size', models.IntegerField()),
                ('source_url', models.URLField()),
                (
                    'ingredient',
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='nutrition.ingredient'
                    )
                ),
                (
                    'license',
                    models.ForeignKey(
                        default=2,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='core.license',
                        verbose_name='License'
                    )
                ),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, wger.utils.helpers.BaseImage),
        ),
        migrations.RunPython(generate_uuids),
    ]