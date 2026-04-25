import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


LIVE_KODI = Path(r"C:\Users\tan\AppData\Roaming\Kodi")
SAVED_BUILD = Path(r"A:\Main User Files\Downloads\KodiBuild\Kodi")
REPO_SKIN_INCLUDE = Path(r"repo\skin.titan.bingie.mod\xml\script-skinshortcuts-includes.xml")


EXPECTED_SKIN_PATHS = {
    "bingiehub-tvshows-510.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_history&tmdb_type=tv",
    "bingiehub-tvshows-520.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_becausemostwatched&tmdb_type=tv",
    "bingiehub-tvshows-560.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_becauseyouwatched&tmdb_type=tv",
    "bingiehub-tvshows-580.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_watchlist&tmdb_type=tv&list_name=Watchlist",
    "bingiehub-movies-510.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_history&tmdb_type=movie",
    "bingiehub-movies-530.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_becausemostwatched&tmdb_type=movie",
    "bingiehub-movies-560.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_becauseyouwatched&tmdb_type=movie",
    "bingiehub-movies-580.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_watchlist&tmdb_type=movie&list_name=Watchlist",
    "bingiehub-mylist-510.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_watchlist&tmdb_type=movie&list_name=Watchlist",
    "bingiehub-mylist-520.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_favorites&tmdb_type=movie&list_name=Favourites",
    "bingiehub-mylist-530.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_watchlist&tmdb_type=tv&list_name=Watchlist",
    "bingiehub-mylist-540.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_favorites&tmdb_type=tv&list_name=Favourites",
    "bingiehub-mylist-550.path": "plugin://plugin.video.themoviedb.helper/?info=trakt_mylists&tmdb_type=both",
}


def profile_roots(kodi_root):
    roots = [kodi_root / "userdata"]
    profiles = kodi_root / "userdata" / "profiles"
    if profiles.exists():
        roots.extend(
            path for path in sorted(profiles.iterdir())
            if path.is_dir() and path.name != "userpicture"
        )
    return roots


def skin_settings(root):
    return root / "addon_data" / "skin.titan.bingie.mod" / "settings.xml"


def shortcuts_file(root, name):
    return root / "addon_data" / "script.skinshortcuts" / name


def setting_map(path):
    tree = ET.parse(path)
    values = {}
    for setting in tree.findall(".//setting"):
        setting_id = setting.attrib.get("id")
        if setting_id:
            values[setting_id] = setting.text or ""
    return values


class TraktWidgetPathTests(unittest.TestCase):
    def test_live_and_saved_skin_settings_use_trakt_widget_sources(self):
        for kodi_root in (LIVE_KODI, SAVED_BUILD):
            for root in profile_roots(kodi_root):
                path = skin_settings(root)
                self.assertTrue(path.exists(), str(path))
                settings = setting_map(path)
                for setting_id, expected in EXPECTED_SKIN_PATHS.items():
                    with self.subTest(path=str(path), setting_id=setting_id):
                        self.assertEqual(settings.get(setting_id), expected)

    def test_live_and_saved_shortcut_data_uses_trakt_sources(self):
        for kodi_root in (LIVE_KODI, SAVED_BUILD):
            for root in profile_roots(kodi_root):
                movies = shortcuts_file(root, "skin.titan.bingie.mod-movies.DATA.xml")
                tvshows = shortcuts_file(root, "skin.titan.bingie.mod-tvshows.DATA.xml")
                self.assertTrue(movies.exists(), str(movies))
                self.assertTrue(tvshows.exists(), str(tvshows))

                movie_text = movies.read_text(encoding="utf-8")
                tv_text = tvshows.read_text(encoding="utf-8")

                self.assertIn("info=trakt_inprogress", movie_text)
                self.assertIn("info=trakt_genres", movie_text)
                self.assertNotIn("list_name=Your+In-Progress&amp;tmdb_id=None&amp;info=trending_week", movie_text)
                self.assertNotIn("info=dir_search&amp;tmdb_type=movie", movie_text)

                self.assertIn("info=trakt_history&amp;tmdb_type=tv", tv_text)
                self.assertIn("info=trakt_inprogress", tv_text)
                self.assertIn("info=trakt_genres", tv_text)
                self.assertNotIn("info=trending_week&amp;tmdb_type=tv", tv_text)
                self.assertNotIn("list_name=Your+In-Progress&amp;tmdb_id=None&amp;info=trending_week", tv_text)
                self.assertNotIn("info=dir_search&amp;tmdb_type=tv", tv_text)

    def test_generated_skin_includes_use_trakt_home_and_progress_widgets(self):
        include_paths = [
            LIVE_KODI / "addons" / "skin.titan.bingie.mod" / "xml" / "script-skinshortcuts-includes.xml",
            SAVED_BUILD / "addons" / "skin.titan.bingie.mod" / "xml" / "script-skinshortcuts-includes.xml",
            REPO_SKIN_INCLUDE,
        ]
        for path in include_paths:
            with self.subTest(path=str(path)):
                self.assertTrue(path.exists(), str(path))
                text = path.read_text(encoding="utf-8")
                self.assertIn("info=trakt_history&amp;tmdb_type=both", text)
                if "Your Recently Watched" in text:
                    self.assertIn("info=trakt_history&amp;tmdb_type=tv", text)
                if "Your+In-Progress" in text:
                    self.assertIn("info=trakt_inprogress", text)
                self.assertNotIn("list_name=Your+In-Progress&amp;tmdb_id=None&amp;info=trending_week", text)

    def test_generated_genre_submenus_use_trakt_genres(self):
        include_paths = [
            LIVE_KODI / "addons" / "skin.titan.bingie.mod" / "xml" / "script-skinshortcuts-includes.xml",
            SAVED_BUILD / "addons" / "skin.titan.bingie.mod" / "xml" / "script-skinshortcuts-includes.xml",
            REPO_SKIN_INCLUDE,
        ]
        for path in include_paths:
            root = ET.parse(path).getroot()
            for item in root.findall(".//item"):
                label = item.findtext("label", "")
                properties = {
                    prop.attrib.get("name"): prop.text or ""
                    for prop in item.findall("property")
                }
                if label != "Genres" or properties.get("group") not in {"movies", "tvshows"}:
                    continue

                values = "\n".join(properties.values())
                with self.subTest(path=str(path), group=properties.get("group")):
                    self.assertIn("info=trakt_genres", values)
                    self.assertNotIn("info=dir_search", values)


if __name__ == "__main__":
    unittest.main()
