from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

def validate_year(value):
    current_year = date.today().year
    if value > current_year:
        raise ValidationError('Year must be greater than or equal to current year.')
    if value < 1895:
        raise ValidationError('Movies were not made before 1895.')


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='posters', blank=True, null=True)
    year_of_release = models.PositiveSmallIntegerField(validators=[validate_year])
    director = models.CharField(max_length=100)
    actors = models.ManyToManyField('Actor',  blank=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'year_of_release'], name='unique_title_and_year_of_release')
        ]
    # def get_actors(self):
    #     return Actor.objects.filter(movie=self)

class Actor(models.Model):
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField('Movie', blank=True)
    def __str__(self):
        return f"{self.name}"
