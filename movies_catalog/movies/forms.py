from django import forms
from .models import Movie, Actor


class MovieForm(forms.ModelForm):

    class Meta:
        model = Movie
        fields = ['title', 'year_of_release', 'description', 'director', 'poster']

    #Custom field for entering actors
    actors = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter up to 4 actors, separated by semicolons.'}),
                             required=False)

    def clean_actors(self):
        actor_names = self.cleaned_data['actors']
        actor_list = [name for name in actor_names.split(';') if name.split()]
        if len(actor_list) > 4:
            raise forms.ValidationError('Too many actors. Up to 4 is allowed.')
        return actor_list

    def save(self, commit=True):
        #Save the movie but don't commit
        movie = super().save(commit=False)

        if commit:
            movie.save() #After this point, the movie has a primary key (id), making it possible to establish relationships with Actor instances.

        #Handle ManyToMany relationship
        actor_names = self.cleaned_data.get('actors')
        if actor_names:
            for name in actor_names:
                actor, created = Actor.objects.get_or_create(name=name)
                if created:
                    movie.actors.add(actor)
        return movie

