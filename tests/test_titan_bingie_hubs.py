import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(r"A:\Development\Version Control\Github\repository.NikeFlix")
SKIN_ROOT = REPO_ROOT / "repo" / "skin.titan.bingie.mod"

HOME_WIDGETS = [
    {
        "id": "2510",
        "name": "Continue Watching",
        "path": "plugin://plugin.video.themoviedb.helper/?info=trakt_history&tmdb_type=both&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_default",
        "limit": "$INFO[Skin.String(WidgetsGlobalLimit)]",
        "sort": "",
    },
    {
        "id": "2520",
        "name": "In Theaters Now",
        "path": "plugin://plugin.video.themoviedb.helper/?info=now_playing&tmdb_type=movie&widget=true&reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]&reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]",
        "style": "widget_layout_default",
        "limit": "$INFO[Skin.String(WidgetsGlobalLimit)]",
        "sort": "",
    },
    {
        "id": "2530",
        "name": "Binge Worthy TV Shows",
        "path": "plugin://plugin.video.themoviedb.helper/?info=random_mostplayed&tmdb_type=tv&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_highlight",
        "limit": "$INFO[Skin.String(WidgetsGlobalLimit)]",
        "sort": "",
    },
    {
        "id": "2540",
        "name": "Watch It Again",
        "path": "plugin://plugin.video.themoviedb.helper/?info=trakt_mostwatched&tmdb_type=movie&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_default",
        "limit": "$NUMBER[50]",
        "sort": "",
    },
    {
        "id": "2550",
        "name": "Top Rated Movies",
        "path": "plugin://plugin.video.themoviedb.helper/?list_name=IMDB%3A+Top+Rated+Movies&list_slug=imdb-top-rated-movies&user_slug=justin&plugin_category=IMDB%3A+Top+Rated+Movies&tmdb_id=None&info=trakt_userlist&sort_by=random&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_default",
        "limit": "$NUMBER[50]",
        "sort": "",
    },
    {
        "id": "2560",
        "name": "Todays Popular TV Shows",
        "path": "plugin://plugin.video.themoviedb.helper/?info=random_popular&tmdb_type=tv&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_default",
        "limit": "$INFO[Skin.String(WidgetsGlobalLimit)]",
        "sort": "",
    },
    {
        "id": "2570",
        "name": "Your Watchlist",
        "path": "plugin://plugin.video.themoviedb.helper/?tmdb_type=both&list_name=Combined+Watchlist&tmdb_id=None&info=trakt_watchlist&sort_by=added&sort_how=desc&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_default",
        "limit": "$INFO[Skin.String(WidgetsGlobalLimit)]",
        "sort": "",
    },
    {
        "id": "2580",
        "name": "Rewatch Some Of Your Favourites",
        "path": "plugin://plugin.video.themoviedb.helper/?tmdb_type=both&list_name=Combined+Favourites&tmdb_id=None&info=trakt_favorites&sort_by=random&reload=%24INFO%5BWindow%28Home%29.Property%28TMDbHelper.Widgets.Reload%29%5D&widget=true",
        "style": "widget_layout_default",
        "limit": "$INFO[Skin.String(WidgetsGlobalLimit)]",
        "sort": "",
    },
]


def read_text(path):
    return path.read_text(encoding="utf-8")


def default_hub_text():
    return read_text(SKIN_ROOT / "xml" / "IncludesDefaultSkinHubs.xml")


def menu_actions_from_shortcuts(path):
    tree = ET.parse(path)
    return [node.text or "" for node in tree.findall(".//shortcut/action")]


def menu_paths_from_generated_skinshortcuts(path):
    tree = ET.parse(path)
    root = tree.getroot()
    mainmenu = root.find(".//include[@name='skinshortcuts-mainmenu']")
    return [
        next(
            (prop.text or "" for prop in item.findall("property") if prop.attrib.get("name") == "path"),
            "",
        )
        for item in mainmenu.findall("item")
    ]


class TitanBingieHubTests(unittest.TestCase):
    def test_main_menu_prioritizes_core_sections_before_live_and_pvr(self):
        expected_order = [
            "ActivateWindow(1109,return)",
            "ActivateWindow(home,return)",
            "ActivateWindow(1111,return)",
            "ActivateWindow(1110,return)",
            "ActivateWindow(1119,return)",
            "ActivateWindow(1114,return)",
            "ActivateWindow(1112,return)",
            "ActivateWindow(1116,return)",
        ]

        source_actions = menu_actions_from_shortcuts(SKIN_ROOT / "shortcuts" / "mainmenu.DATA.xml")
        generated_paths = menu_paths_from_generated_skinshortcuts(
            SKIN_ROOT / "xml" / "script-skinshortcuts-includes.xml"
        )

        for actions in [source_actions, generated_paths]:
            with self.subTest(actions=actions):
                positions = [actions.index(action) for action in expected_order]
                self.assertEqual(sorted(positions), positions)
                self.assertEqual(0, actions.index("ActivateWindow(1109,return)"))
                self.assertEqual(1, actions.index("ActivateWindow(home,return)"))

    def test_sports_hub_uses_separate_sport_specific_rows(self):
        text = default_hub_text()

        for expected in [
            "group_key=basketball",
            "group_key=hockey",
            "group_key=nfl",
            "group_key=cfl",
            "group_key=formula_one",
            "group_key=nascar",
            "group_key=wrestling",
            "group_key=soccer_all",
        ]:
            self.assertIn(expected, text)

        for old_value in [
            "More Sports - CFL / F1 / NASCAR / WWE",
            "group_key=espn_channels",
            "group_key=tnt_channels",
            "section=news",
            "section=soccer",
        ]:
            self.assertNotIn(old_value, text)

    def test_live_sports_hub_uses_pvr_style_layout_and_art(self):
        hub_text = read_text(SKIN_ROOT / "xml" / "Custom_1112_New_Hub.xml")
        includes_text = read_text(SKIN_ROOT / "xml" / "IncludesHubs.xml")

        self.assertIn("BingieSpotlightCornerImage", hub_text)
        self.assertIn("special://skin/extras/media/backgrounds/live_sports.jpg", hub_text)
        self.assertIn("bingie_items_live_sports", hub_text)
        self.assertNotIn("<include>HomeBingie</include>", hub_text)
        self.assertIn('<include name="bingie_items_live_sports">', includes_text)
        self.assertIn('widgetStyle" value="widget_layout_landscape"', includes_text)

    def test_live_sports_primary_rows_use_horizontal_landscape_layout(self):
        hubs = ET.parse(SKIN_ROOT / "xml" / "IncludesHubs.xml").getroot()
        primary_widgets = {"1510", "1520", "1530", "1540"}
        styles = {}
        for include in hubs.findall(".//include[@content='widget_base_normal']"):
            params = {
                param.attrib.get("name"): param.attrib.get("value", "")
                for param in include.findall("param")
            }
            if (
                params.get("widgetid") in primary_widgets
                and params.get("widgetPath", "").startswith("plugin://plugin.video.giptv/")
                and "group_key=" in params.get("widgetPath", "")
            ):
                styles[params["widgetName"]] = params.get("widgetStyle")

        for widget_name in ["NBA / Basketball", "NHL / Hockey", "NFL", "CFL"]:
            self.assertEqual("widget_layout_landscape", styles[widget_name])

    def test_hub_widget_styles_resolve_to_existing_skin_includes(self):
        hubs = ET.parse(SKIN_ROOT / "xml" / "IncludesHubs.xml").getroot()
        home_widgets = ET.parse(SKIN_ROOT / "xml" / "IncludesHomeWidgets.xml").getroot()
        defined_styles = {
            node.attrib["name"]
            for node in home_widgets.findall(".//include")
            if node.attrib.get("name", "").startswith("widget_layout_")
        }

        used_styles = {
            param.attrib["value"]
            for param in hubs.findall(".//param[@name='widgetStyle']")
            if param.attrib.get("value", "").startswith("widget_layout_")
        }

        self.assertFalse(used_styles - defined_styles)

    def test_livetv_shortcuts_open_pvr_windows(self):
        path = SKIN_ROOT / "shortcuts" / "livetv.DATA.xml"
        tree = ET.parse(path)
        actions = [node.text or "" for node in tree.findall(".//action")]

        self.assertIn("ActivateWindow(TVGuide)", actions)
        self.assertIn("ActivateWindow(TVChannels)", actions)
        self.assertIn("ActivateWindow(TVRecordings,return)", actions)
        self.assertTrue(all("plugin.video.giptv" not in action for action in actions))

    def test_power_menu_uses_quit_instead_of_system_shutdown(self):
        for path in [
            SKIN_ROOT / "xml" / "DialogButtonMenu.xml",
            SKIN_ROOT / "xml" / "script-skinshortcuts-includes.xml",
        ]:
            text = read_text(path)
            self.assertIn("Quit()", text)
            self.assertNotIn("<onclick>ShutDown</onclick>", text)
            self.assertNotIn("<onclick>PowerDown</onclick>", text)

    def test_pvr_hub_uses_pvr_client_and_holds_general_guide_widgets(self):
        text = read_text(SKIN_ROOT / "xml" / "IncludesHubs.xml")

        for expected in [
            'widgetPath" value="pvr://channels/tv/*?view=lastplayed"',
            'widgetPath" value="pvr://channels/tv/*"',
            'widgetName" value="ESPN Channels"',
            "group_key=espn_channels",
            'widgetName" value="TNT / TBS / truTV"',
            "group_key=tnt_channels",
            'widgetName" value="News &amp; Local"',
            "section=news",
        ]:
            self.assertIn(expected, text)

    def test_pvr_and_live_sports_backdrops_are_packaged_with_skin(self):
        for filename in ["live_sports.jpg", "pvr_hub.jpg"]:
            path = SKIN_ROOT / "extras" / "media" / "backgrounds" / filename
            self.assertTrue(path.exists(), filename)
            self.assertGreater(path.stat().st_size, 10000, filename)

    def test_home_widgets_use_current_tmdbhelper_profile_settings(self):
        path = SKIN_ROOT / "xml" / "script-skinshortcuts-includes.xml"
        tree = ET.parse(path)
        root = tree.getroot()

        home_item = None
        for item in root.findall(".//include[@name='skinshortcuts-mainmenu']/item"):
            properties = {
                prop.attrib.get("name"): prop.text or ""
                for prop in item.findall("property")
            }
            if properties.get("defaultID") == "10000":
                home_item = properties
                break

        self.assertIsNotNone(home_item)

        for index, widget in enumerate(HOME_WIDGETS):
            suffix = "" if index == 0 else f".{index}"
            self.assertEqual("Addon", home_item[f"widget{suffix}"])
            self.assertEqual("videos", home_item[f"widgetTarget{suffix}"])
            self.assertEqual(widget["name"], home_item[f"widgetName{suffix}"])
            self.assertEqual(widget["path"], home_item[f"widgetPath{suffix}"])

        widget_blocks = {
            params["widgetid"]: params
            for include in root.findall(".//include[@content='widget_base']")
            for params in [
                {
                    param.attrib.get("name"): param.attrib.get("value", "")
                    for param in include.findall("param")
                }
            ]
            if params.get("submenuid") == "num-10000"
        }

        label_values = {
            value.attrib.get("condition", ""): value.text or ""
            for variable in root.findall(".//variable[@name='widgetlabel-2']")
            for value in variable.findall("value")
        }

        for index, widget in enumerate(HOME_WIDGETS):
            with self.subTest(widget=widget["id"]):
                params = widget_blocks[widget["id"]]
                self.assertEqual(widget["name"], params["widgetName"])
                self.assertEqual(widget["path"], params["widgetPath"])
                self.assertEqual(widget["style"], params["widgetStyle"])
                self.assertEqual(widget["sort"], params["widgetSortBy"])
                self.assertEqual(widget["limit"], params["widgetLimit"])

                refresh = root.find(f".//variable[@name='{widget['id']}-refresh']")
                self.assertIsNotNone(refresh)
                default_value = next(
                    value.text or ""
                    for value in refresh.findall("value")
                    if "condition" not in value.attrib
                )
                self.assertEqual(widget["path"], default_value)

                label_condition = (
                    "" if index == 0 else f"String.IsEqual(Skin.String(widgetvalue-num-10000),{index})"
                )
                self.assertEqual(widget["name"], label_values[label_condition])

        home_section = read_text(path).split('<include name="skinshortcuts-template-Widgets-Master user">', 1)[1]
        home_section = home_section.split('<variable name="widgetinfolabel-2580">', 1)[0]
        self.assertNotIn("script.skin.helper.widgets", home_section)
        self.assertNotIn("similarshowsandmovies", home_section)


if __name__ == "__main__":
    unittest.main()
