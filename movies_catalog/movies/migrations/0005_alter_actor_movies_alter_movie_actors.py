# Generated by Django 5.1.4 on 2024-12-25 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_rename_models_actor_movies_alter_movie_actors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='movies',
            field=models.ManyToManyField(to='movies.movie'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='actors',
            field=models.ManyToManyField(to='movies.actor'),
        ),
    ]
