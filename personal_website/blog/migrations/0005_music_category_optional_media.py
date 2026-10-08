from django.db import migrations, models


def rename_food_category(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Post.objects.using(schema_editor.connection.alias).filter(category='comida').update(category='musica')


def restore_food_category(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Post.objects.using(schema_editor.connection.alias).filter(category='musica').update(category='comida')


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_move_post_media_to_img'),
    ]

    operations = [
        migrations.RunPython(rename_food_category, restore_food_category),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(
                choices=[
                    ('deportes', 'Deportes'),
                    ('musica', 'Música'),
                    ('desarrollo web', 'Desarrollo web'),
                    ('gaming', 'Gaming'),
                ],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='media',
            field=models.FileField(blank=True, upload_to='img/'),
        ),
    ]
