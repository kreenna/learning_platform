from rest_framework import serializers

def validate_youtube_link(link):
    if "www.youtube.com" not in link:
        raise serializers.ValidationError("The link must be to a YouTube video.")

