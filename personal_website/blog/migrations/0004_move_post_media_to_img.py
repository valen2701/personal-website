from django.db import migrations, models


def move_post_media(apps, schema_editor, source_prefix, target_prefix):
    Post = apps.get_model('blog', 'Post')
    database = schema_editor.connection.alias
    storage = Post._meta.get_field('media').storage

    for post_id, media_name in Post.objects.using(database).values_list('pk', 'media'):
        if not media_name.startswith(source_prefix):
            continue

        target_name = target_prefix + media_name[len(source_prefix):]
        if storage.exists(media_name):
            if storage.exists(target_name):
                storage.delete(media_name)
            else:
                with storage.open(media_name, 'rb') as source_file:
                    target_name = storage.save(target_name, source_file)
                storage.delete(media_name)

        Post.objects.using(database).filter(pk=post_id).update(media=target_name)


def move_media_to_img(apps, schema_editor):
    move_post_media(apps, schema_editor, 'blog/', 'img/')


def move_media_to_blog(apps, schema_editor):
    move_post_media(apps, schema_editor, 'img/', 'blog/')


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_commentlike_postlike'),
    ]

    operations = [
        migrations.RunPython(move_media_to_img, move_media_to_blog),
        migrations.AlterField(
            model_name='post',
            name='media',
            field=models.FileField(upload_to='img/'),
        ),
    ]
