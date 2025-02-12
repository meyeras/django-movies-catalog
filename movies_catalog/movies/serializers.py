from rest_framework import serializers
from .models import Movie, Actor

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name']  # Used in GET response

class MovieSerializer(serializers.ModelSerializer):
    actors = serializers.SerializerMethodField()  # Handles GET response

    class Meta:
        model = Movie
        fields = '__all__'

    def get_actors(self, obj):
        """Handles GET response - returns actors as a list of {'id', 'name'}"""
        return ActorSerializer(obj.actors.all(), many=True).data

    def create(self, validated_data):
        """Handles POST request - expects a list of actor names"""
        actor_names = validated_data.pop('actors', [])
        movie = Movie.objects.create(**validated_data)


        # Create or get actors
        if isinstance(actor_names, list):  # Ensure it's a list
            for name in actor_names:
                actor, _ = Actor.objects.get_or_create(name=name.strip())
                movie.actors.add(actor)

        return movie