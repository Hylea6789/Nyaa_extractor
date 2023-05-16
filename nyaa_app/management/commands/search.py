from django.core.management.base import BaseCommand
from django_server.nyaa_app.models import SearchEntry
from pathlib import Path
from NyaaPy.nyaa import Nyaa
from NyaaPy import torrent
import requests
import re

PATH_TORRENT: Path = Path(__file__).parent.parent.parent.parent / "torrents"

class Command(BaseCommand):
    help = 'Prints the titles of all Posts'

    def handle(self, *args, **options):
        parameter_sql: ParameterSQL = ParameterSQL()
        parameter_sql.read_sql()
        parameter_sql.download_torrent()


class RegularSearch:
    # handles search on the nyaa.si website and return a Torrent object
    def __init__(
            self,
            search_entry: SearchEntry,
    ):
        self.entry: SearchEntry = search_entry

    def search(self) -> torrent:
        # searches a data on nyaa.si from the parameters it was specified
        nyaa = Nyaa()
        # TODO add quality + format
        keyword = f"{self.entry.name} {self.entry.trad_team} {self.entry.video_format} {self.entry.quality}"
        results_list: list[torrent] = nyaa.search(
            keyword=f"{str(self.entry.season)} {str(self.entry.episode)} {keyword}"
        )

        # searches if there is one result that is the episode searched
        result: torrent = self.search_result(results_list)

        # if episode + 1 is not available, searches for the 1st episode of the next season
        if not result:
            results_list = nyaa.search(
                keyword=f"{keyword} {str(self.entry.season + 1)} 1"
            )
            result = self.search_result(results_list)
        return result

    def search_result(self, results: list[torrent]) -> torrent:
        if not results:
            return None

        # checks if the ep number and season check a certain pattern with regex
        regex = f"(- 0?{self.entry.episode})|(S0?{self.entry.season}E0?{self.entry.episode})"
        for result in results:
            if re.search(regex, result.name):
                return result
        return None


class ParameterSQL:
    def __init__(self):
        self._torrent_list: list[torrent] = []

    def read_sql(self):
        for entry in SearchEntry.objects.all():
            self.process_entry(entry)

    def process_entry(self, entry: SearchEntry):
        # process one entry of the SQL databases

        print(entry)

        # while a new episode might be available
        has_new_episode = True
        while has_new_episode:
            regular_search = RegularSearch(entry)
            result = regular_search.search()

            # there is no episode available
            if result is None:
                has_new_episode = False
            # there is an episode available
            # increment the episode number to search for the next one
            else:
                entry.episode += 1
                self._torrent_list.append(result)
            entry.save()

    def download_torrent(self):
        # downloads torrents from the torrents list
        print("---Torrent downloaded---")
        for torrent in self._torrent_list:
            download_url = torrent.download_url
            r = requests.get(download_url, allow_redirects=True)
            open(PATH_TORRENT / f"{torrent.name}.torrent", "wb").write(r.content)
            print(f'"{torrent.name}" downloaded')
        print(f"total : {str(len(self._torrent_list))} torrents downloaded")
