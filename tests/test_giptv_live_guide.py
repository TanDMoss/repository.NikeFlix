import sys
import unittest
from pathlib import Path


GIPTV_ROOT = Path(r"C:\Users\tan\AppData\Roaming\Kodi\addons\plugin.video.giptv")
sys.path.insert(0, str(GIPTV_ROOT))


from resources.lib import live_guide  # noqa: E402


class LiveGuideTaxonomyTests(unittest.TestCase):
    def test_basketball_group_matches_major_nba_channels(self):
        streams = [
            {"stream_id": 1, "name": "NBA League Pass 01", "category_name": "USA Sports"},
            {"stream_id": 2, "name": "ESPN US", "category_name": "Sports Networks"},
            {"stream_id": 3, "name": "Prime Video NBA", "category_name": "Sports"},
            {"stream_id": 4, "name": "CTV Calgary", "category_name": "Canada News"},
            {"stream_id": 5, "name": "ESPN Deportes", "category_name": "USA Sports"},
            {"stream_id": 6, "name": "TNT Series", "category_name": "US Entertainment"},
        ]

        matches = live_guide.match_streams(streams, "basketball")

        self.assertEqual(
            [item["name"] for item in matches],
            ["NBA League Pass 01", "Prime Video NBA", "ESPN US"],
        )

    def test_news_local_group_matches_requested_canadian_markets(self):
        streams = [
            {"stream_id": 1, "name": "CBC Calgary", "category_name": "Canada News"},
            {"stream_id": 2, "name": "Global Lethbridge", "category_name": "Local"},
            {"stream_id": 3, "name": "NTV Newfoundland", "category_name": "Canada"},
            {"stream_id": 4, "name": "NBA TV Canada", "category_name": "Sports"},
        ]

        matches = live_guide.match_streams(streams, "canada_local_news")

        self.assertEqual(
            [item["name"] for item in matches],
            ["CBC Calgary", "Global Lethbridge", "NTV Newfoundland"],
        )

    def test_reality_group_matches_lifestyle_reality_channels(self):
        streams = [
            {"stream_id": 1, "name": "Bravo East", "category_name": "US Entertainment"},
            {"stream_id": 2, "name": "TLC Canada", "category_name": "Canada"},
            {"stream_id": 3, "name": "HGTV UK", "category_name": "UK Lifestyle"},
            {"stream_id": 4, "name": "Sky Sports Main Event", "category_name": "UK Sports"},
        ]

        matches = live_guide.match_streams(streams, "reality_lifestyle")

        self.assertEqual(
            [item["name"] for item in matches],
            ["Bravo East", "HGTV UK", "TLC Canada"],
        )

    def test_section_groups_are_stable_for_skin_widgets(self):
        keys = [group["key"] for group in live_guide.groups_for_section("sports")]

        for expected in [
            "espn_channels",
            "tnt_channels",
            "canadian_sports",
            "nfl",
            "cfl",
            "basketball",
            "hockey",
            "formula_one",
            "nascar",
            "soccer_premier_league",
            "soccer_mls",
            "wrestling",
            "mma_boxing",
        ]:
            self.assertIn(expected, keys)

    def test_espn_and_tnt_groups_stay_separate(self):
        streams = [
            {"stream_id": 1, "name": "ESPN US", "category_name": "USA Sports"},
            {"stream_id": 2, "name": "ESPN 2 Canada", "category_name": "Canada Sports"},
            {"stream_id": 3, "name": "TNT Sports 1 UK", "category_name": "UK Sports"},
            {"stream_id": 4, "name": "TBS US", "category_name": "USA Entertainment"},
            {"stream_id": 5, "name": "ESPN Deportes", "category_name": "USA Sports"},
        ]

        espn = live_guide.match_streams(streams, "espn_channels")
        tnt = live_guide.match_streams(streams, "tnt_channels")

        self.assertEqual([item["name"] for item in espn], ["ESPN 2 Canada", "ESPN US"])
        self.assertEqual([item["name"] for item in tnt], ["TBS US", "TNT Sports 1 UK"])

    def test_nfl_and_cfl_are_separate(self):
        streams = [
            {"stream_id": 1, "name": "NFL Network US", "category_name": "USA Sports"},
            {"stream_id": 2, "name": "CBS Sports Network", "category_name": "USA Sports"},
            {"stream_id": 3, "name": "CFL Plus", "category_name": "Canada Sports"},
            {"stream_id": 4, "name": "TSN 1", "category_name": "Canada Sports"},
        ]

        nfl = live_guide.match_streams(streams, "nfl")
        cfl = live_guide.match_streams(streams, "cfl")

        self.assertEqual([item["name"] for item in nfl], ["NFL Network US", "CBS Sports Network"])
        self.assertEqual([item["name"] for item in cfl], ["CFL Plus", "TSN 1", "CBS Sports Network"])

    def test_canadian_sports_excludes_french_language_networks(self):
        streams = [
            {"stream_id": 1, "name": "TSN 1", "category_name": "Canada Sports"},
            {"stream_id": 2, "name": "Sportsnet One", "category_name": "Canada Sports"},
            {"stream_id": 3, "name": "RDS", "category_name": "Canada Sports"},
        ]

        matches = live_guide.match_streams(streams, "canadian_sports")

        self.assertEqual([item["name"] for item in matches], ["TSN 1", "Sportsnet One"])

    def test_motorsports_and_wrestling_groups_exist(self):
        streams = [
            {"stream_id": 1, "name": "Sky Sports F1 UK", "category_name": "UK Sports"},
            {"stream_id": 2, "name": "NASCAR Channel US", "category_name": "USA Sports"},
            {"stream_id": 3, "name": "WWE Network", "category_name": "USA Sports"},
            {"stream_id": 4, "name": "AEW Plus", "category_name": "US Sports"},
        ]

        self.assertEqual(
            [item["name"] for item in live_guide.match_streams(streams, "formula_one")],
            ["Sky Sports F1 UK"],
        )
        self.assertEqual(
            [item["name"] for item in live_guide.match_streams(streams, "nascar")],
            ["NASCAR Channel US"],
        )
        self.assertEqual(
            [item["name"] for item in live_guide.match_streams(streams, "wrestling")],
            ["AEW Plus", "WWE Network"],
        )

    def test_non_english_and_non_us_ca_uk_channels_are_filtered(self):
        streams = [
            {"stream_id": 1, "name": "TSN 1", "category_name": "Canada Sports"},
            {"stream_id": 2, "name": "Sky Sports Main Event", "category_name": "UK Sports"},
            {"stream_id": 3, "name": "Sky Sport Bundesliga", "category_name": "DE Sports"},
            {"stream_id": 4, "name": "beIN Sports France", "category_name": "FR Sports"},
            {"stream_id": 5, "name": "ESPN Deportes", "category_name": "USA Sports"},
        ]

        matches = live_guide.match_streams(streams, "sports_all")

        self.assertEqual(
            [item["name"] for item in matches],
            ["Sky Sports Main Event", "TSN 1"],
        )


if __name__ == "__main__":
    unittest.main()
