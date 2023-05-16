from django.db import models


class SearchEntry(models.Model):
    # stores the entry to search on Nyaa.si

    class Quality(models.TextChoices):
        Q480P = "480p"
        Q720P = "720p"
        Q1080P = "1080p"

        def __str__(self):
            return self.name

    class VideoFormat(models.TextChoices):
        MKV = "mkv"
        MP4 = "mp4"

    name = models.CharField(max_length=200)
    episode = models.IntegerField()
    season = models.IntegerField()
    language = models.CharField(
        max_length=200,
        blank=True
    )
    trad_team = models.CharField(
        max_length=200,
        blank=True
    )

    quality = models.CharField(
        choices=Quality.choices,
        default=Quality.Q1080P,
        max_length = 200
    )

    video_format = models.CharField(
        choices=VideoFormat.choices,
        default=VideoFormat.MKV,
        max_length = 200
    )

    def __str__(self):
        return self.name
