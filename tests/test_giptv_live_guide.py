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
            {"stream_id": 7, "name": "AF NBA TV", "category_name": "AF Sports"},
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
            "nfl",
            "cfl",
            "basketball",
            "hockey",
            "formula_one",
            "nascar",
            "wrestling",
            "mma_boxing",
        ]:
            self.assertIn(expected, keys)

        self.assertNotIn("soccer_premier_league", keys)

    def test_soccer_leagues_have_their_own_section(self):
        keys = [group["key"] for group in live_guide.groups_for_section("soccer")]

        self.assertEqual(
            keys,
            [
                "soccer_all",
                "soccer_premier_league",
                "soccer_mls",
                "soccer_champions_league",
            ],
        )

    def test_soccer_hub_uses_one_all_leagues_group(self):
        group = live_guide.get_group("soccer_all")

        self.assertIsNotNone(group)
        self.assertIn("premier league", group["terms"])
        self.assertIn("mls", group["terms"])
        self.assertIn("champions league", group["terms"])
        self.assertEqual(group["label"], "Soccer")

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

    def test_canada_and_us_sports_channels_sort_before_au_general_channels(self):
        streams = [
            {"stream_id": 1, "name": "AU ESPN 1", "category_name": "Australia Sports"},
            {"stream_id": 2, "name": "ESPN US", "category_name": "USA Sports"},
            {"stream_id": 3, "name": "CA ESPN 2", "category_name": "Canada Sports"},
            {"stream_id": 4, "name": "UK ESPN Classic", "category_name": "UK Sports"},
        ]

        matches = live_guide.match_streams(streams, "espn_channels")

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in matches],
            ["ESPN 2", "ESPN US", "ESPN Classic", "ESPN 1"],
        )

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
            ["WWE Network", "AEW Plus"],
        )

    def test_formula_one_prefers_f1_specific_coverage_before_region(self):
        streams = [
            {"stream_id": 1, "name": "ESPN US", "category_name": "USA Sports"},
            {"stream_id": 2, "name": "TSN 1 Canada", "category_name": "Canada Sports"},
            {"stream_id": 3, "name": "Sky Sports F1 UK", "category_name": "UK Sports"},
            {"stream_id": 4, "name": "F1 TV", "category_name": "USA Sports"},
        ]

        matches = live_guide.match_streams(streams, "formula_one")

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in matches],
            ["Sky Sports F1 UK", "F1 TV"],
        )

    def test_wrestling_official_channels_sort_before_general_networks(self):
        streams = [
            {"stream_id": 1, "name": "USA Network WWE Raw", "category_name": "USA Entertainment"},
            {"stream_id": 2, "name": "AEW Plus", "category_name": "US Sports"},
            {"stream_id": 3, "name": "WWE Network", "category_name": "USA Sports"},
            {"stream_id": 4, "name": "TNT Sports AEW", "category_name": "UK Sports"},
            {"stream_id": 5, "name": "AF WWE Network", "category_name": "AF Sports"},
            {"stream_id": 6, "name": "AR CTV RAW", "category_name": "AR Entertainment"},
            {"stream_id": 8, "name": "AR WWE Shahid VIP PPV", "category_name": "AR Sports"},
            {"stream_id": 9, "name": "MY WWE Network", "category_name": "MY Sports"},
            {"stream_id": 10, "name": "DSTV WWE Superslam", "category_name": "Sports"},
            {"stream_id": 11, "name": "OSN WWE f", "category_name": "Sports"},
            {"stream_id": 12, "name": "F ALWAN WWE", "category_name": "Sports"},
            {
                "stream_id": 7,
                "name": "Flowrestling 2026 Canadian Wrestling Champs",
                "category_name": "Canada Sports",
            },
        ]

        matches = live_guide.match_streams(streams, "wrestling")

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in matches],
            ["WWE Network", "AEW Plus", "USA Network WWE Raw", "TNT Sports AEW"],
        )

    def test_clean_league_channels_sort_before_provider_prefixed_league_channels(self):
        streams = [
            {"stream_id": 1, "name": "SLING NFL Network RAW", "category_name": "US Sports"},
            {"stream_id": 2, "name": "NFL RedZone US", "category_name": "USA Sports"},
            {"stream_id": 3, "name": "NFL Network US", "category_name": "USA Sports"},
            {"stream_id": 4, "name": "CBS Sports Network", "category_name": "USA Sports"},
            {"stream_id": 5, "name": "PRIME NBA TV RAW", "category_name": "US Sports"},
            {"stream_id": 6, "name": "NBA TV Canada", "category_name": "Canada Sports"},
            {"stream_id": 7, "name": "NBA League Pass 01", "category_name": "USA Sports"},
            {"stream_id": 8, "name": "ESPN US", "category_name": "USA Sports"},
            {"stream_id": 9, "name": "PRIME WWE Network RAW", "category_name": "US Sports"},
            {"stream_id": 10, "name": "WWE Network", "category_name": "USA Sports"},
            {"stream_id": 11, "name": "AEW Plus", "category_name": "US Sports"},
            {"stream_id": 12, "name": "TNT Sports AEW", "category_name": "UK Sports"},
            {"stream_id": 13, "name": "WWE", "category_name": "USA Sports"},
            {"stream_id": 14, "name": "Wrestling AEW Collision", "category_name": "US Sports"},
        ]

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in live_guide.match_streams(streams, "nfl")],
            ["NFL Network US", "NFL RedZone US", "SLING NFL Network RAW", "CBS Sports Network", "ESPN US"],
        )
        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in live_guide.match_streams(streams, "basketball")],
            ["NBA League Pass 01", "NBA TV Canada", "PRIME NBA TV RAW", "ESPN US"],
        )
        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in live_guide.match_streams(streams, "wrestling")],
            [
                "WWE Network",
                "AEW Plus",
                "WWE",
                "PRIME WWE Network RAW",
                "Wrestling AEW Collision",
                "TNT Sports AEW",
            ],
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
            ["TSN 1", "Sky Sports Main Event"],
        )

    def test_region_code_noise_is_filtered_before_matching_sports(self):
        streams = [
            {"stream_id": 1, "name": "FR beIN Sports 1", "category_name": "FR Sports"},
            {"stream_id": 2, "name": "DE Sky Sport F1", "category_name": "DE Sports"},
            {"stream_id": 3, "name": "ES ESPN Deportes", "category_name": "ES Sports"},
            {"stream_id": 4, "name": "UK Sky Sports F1", "category_name": "UK Sports"},
            {"stream_id": 5, "name": "CA TSN 1", "category_name": "Canada Sports"},
        ]

        matches = live_guide.match_streams(streams, "sports_all")

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in matches],
            ["Sky Sports F1", "TSN 1"],
        )

    def test_primary_sport_named_channels_sort_before_general_networks(self):
        streams = [
            {"stream_id": 1, "name": "ESPN US", "category_name": "USA Sports"},
            {"stream_id": 2, "name": "TSN 1", "category_name": "Canada Sports"},
            {"stream_id": 3, "name": "Sportsnet One", "category_name": "Canada Sports"},
            {"stream_id": 4, "name": "NBA TV Canada", "category_name": "Canada Sports"},
            {"stream_id": 5, "name": "NBA League Pass 01", "category_name": "USA Sports"},
            {"stream_id": 6, "name": "Prime Video NBA", "category_name": "US Sports"},
            {"stream_id": 7, "name": "ESPN Deportes", "category_name": "USA Sports"},
            {"stream_id": 8, "name": "AF NBA TV", "category_name": "AF Sports"},
        ]

        matches = live_guide.match_streams(streams, "basketball")

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in matches],
            [
                "NBA League Pass 01",
                "NBA TV Canada",
                "Prime Video NBA",
                "ESPN US",
                "TSN 1",
                "Sportsnet One",
            ],
        )

    def test_nfl_named_channels_sort_before_general_networks_and_exclude_af(self):
        streams = [
            {"stream_id": 1, "name": "ESPN US", "category_name": "USA Sports"},
            {"stream_id": 2, "name": "CBS Sports Network", "category_name": "USA Sports"},
            {"stream_id": 3, "name": "NFL RedZone US", "category_name": "USA Sports"},
            {"stream_id": 4, "name": "NFL Network US", "category_name": "USA Sports"},
            {"stream_id": 5, "name": "AF NFL Network", "category_name": "AF Sports"},
        ]

        matches = live_guide.match_streams(streams, "nfl")

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in matches],
            ["NFL Network US", "NFL RedZone US", "CBS Sports Network", "ESPN US"],
        )

    def test_league_channels_sort_first_for_nhl_cfl_and_nfl(self):
        streams = [
            {"stream_id": 1, "name": "TSN 1", "category_name": "Canada Sports"},
            {"stream_id": 2, "name": "Sportsnet One", "category_name": "Canada Sports"},
            {"stream_id": 3, "name": "NHL Network US", "category_name": "USA Sports"},
            {"stream_id": 4, "name": "CFL Plus", "category_name": "Canada Sports"},
            {"stream_id": 5, "name": "NFL RedZone US", "category_name": "USA Sports"},
            {"stream_id": 6, "name": "CBS Sports Network", "category_name": "USA Sports"},
        ]

        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in live_guide.match_streams(streams, "hockey")],
            ["NHL Network US", "Sportsnet One", "TSN 1"],
        )
        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in live_guide.match_streams(streams, "cfl")],
            ["CFL Plus", "TSN 1", "CBS Sports Network"],
        )
        self.assertEqual(
            [live_guide.clean_display_name(item["name"]) for item in live_guide.match_streams(streams, "nfl")],
            ["NFL RedZone US", "CBS Sports Network"],
        )

    def test_clean_display_name_removes_markup_region_tags_and_quality_noise(self):
        examples = {
            "[B][COLOR green][LIVE][/COLOR][/B] [US] NBA TV FHD": "NBA TV",
            "USA: ESPN 2 HD": "ESPN 2",
            "CA | TSN 1 1080p": "TSN 1",
            "UK - Sky Sports F1 UHD": "Sky Sports F1",
            "[LIVE] [US] [1080p] WWE Network": "WWE Network",
        }

        for raw, expected in examples.items():
            self.assertEqual(live_guide.clean_display_name(raw), expected)

    def test_clean_description_removes_bracket_markup_and_quality_noise(self):
        self.assertEqual(
            live_guide.clean_description("[COLOR yellow][CA][/COLOR] Sports [1080p]"),
            "Sports",
        )

    def test_news_section_has_separate_city_and_country_groups(self):
        keys = [group["key"] for group in live_guide.groups_for_section("news")]

        for expected in [
            "calgary_news",
            "lethbridge_news",
            "newfoundland_news",
            "canada_news",
            "us_news",
            "uk_news",
        ]:
            self.assertIn(expected, keys)


if __name__ == "__main__":
    unittest.main()
