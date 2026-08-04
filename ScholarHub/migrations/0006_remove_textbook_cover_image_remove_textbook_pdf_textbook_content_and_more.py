from django.db import migrations, models
import django.db.models.deletion


def migrate_textbook_content(apps, schema_editor):
    Textbook = apps.get_model('ScholarHub', 'Textbook')
    for textbook in Textbook.objects.all():
        content_parts = []
        if textbook.description:
            content_parts.append(textbook.description)
        if textbook.title:
            content_parts.append(f'Title: {textbook.title}')
        if textbook.author:
            content_parts.append(f'Author: {textbook.author}')
        textbook.content = '\n\n'.join(part for part in content_parts if part)
        textbook.save(update_fields=['content'])


class Migration(migrations.Migration):

    dependencies = [
        ('ScholarHub', '0005_alter_course_options_alter_course_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='textbook',
            name='content',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.RunPython(migrate_textbook_content, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='textbook',
            name='cover_image',
        ),
        migrations.RemoveField(
            model_name='textbook',
            name='pdf',
        ),
        migrations.AlterField(
            model_name='textbook',
            name='description',
            field=models.TextField(blank=True, help_text='Short summary shown on the cards.'),
        ),
        migrations.AlterField(
            model_name='textbook',
            name='title',
            field=models.CharField(max_length=220),
        ),
        migrations.AlterField(
            model_name='textbook',
            name='author',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='textbook',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='textbooks', to='ScholarHub.course'),
        ),
    ]
