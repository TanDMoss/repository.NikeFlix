import unittest
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


GIPTV_ROOT = Path(r"C:\Users\tan\AppData\Roaming\Kodi\addons\plugin.video.giptv")
SAVED_BUILD_GIPTV_ROOT = Path(
    r"A:\Main User Files\Downloads\KodiBuild\Kodi\addons\plugin.video.giptv"
)
PVR_SETTINGS = Path(
    r"C:\Users\tan\AppData\Roaming\Kodi\userdata\addon_data\pvr.iptvsimple\instance-settings-1.xml"
)
SAVED_BUILD_PVR_SETTINGS = Path(
    r"A:\Main User Files\Downloads\KodiBuild\Kodi\userdata\addon_data\pvr.iptvsimple\instance-settings-1.xml"
)
NIKE_REPO_GIPTV_ROOT = Path(
    r"A:\Development\Version Control\Github\repository.NikeFlix\repo\plugin.video.giptv"
)
FAMILY_REPO_GIPTV_ROOT = Path(
    r"A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\plugin.video.giptv"
)
NIKE_UPLOAD_ZIP = Path(r"A:\Main User Files\Downloads\Kodi Builds\nikeflixwizard.zip")
FAMILY_UPLOAD_ZIP = Path(
    r"A:\Main User Files\Downloads\Kodi Builds\nikeflixfamilywizard.zip"
)
TARGET_GIPTV_VERSION = "2.9.4"


class GiptvServiceStartupTests(unittest.TestCase):
    def test_pvr_simple_uses_local_xtream_playlist_bridge(self):
        expected_path = "special://profile/addon_data/pvr.iptvsimple/giptv-live.m3u"

        for addon_root in [GIPTV_ROOT, SAVED_BUILD_GIPTV_ROOT]:
            with self.subTest(addon_root=str(addon_root)):
                service_text = (addon_root / "service.py").read_text(encoding="utf-8")
                bridge_text = (
                    addon_root / "resources" / "lib" / "pvr_bridge.py"
                ).read_text(encoding="utf-8")

                self.assertIn("from resources.lib.pvr_bridge import ensure_pvr_playlist_ready", service_text)
                self.assertIn("ensure_pvr_playlist_ready()", service_text)
                self.assertIn("#EXTM3U", bridge_text)
                self.assertIn("xtream_api.get_live_streams()", bridge_text)
                self.assertIn("xtream_api.categories(xtream_api.LIVE_TYPE)", bridge_text)
                self.assertIn("live_guide.is_supported_region_stream(stream)", bridge_text)
                self.assertIn(expected_path, bridge_text)

        for settings_path in [PVR_SETTINGS, SAVED_BUILD_PVR_SETTINGS]:
            with self.subTest(settings_path=str(settings_path)):
                settings = {
                    node.attrib["id"]: (node.text or "").strip()
                    for node in ET.parse(settings_path).getroot().findall("setting")
                }

                self.assertEqual("0", settings["m3uPathType"])
                self.assertEqual(expected_path, settings["m3uPath"])
                self.assertEqual("", settings["m3uUrl"])

    def test_giptv_deferred_startup_delay_keeps_live_sections_responsive(self):
        for addon_root in [GIPTV_ROOT, SAVED_BUILD_GIPTV_ROOT]:
            with self.subTest(addon_root=str(addon_root)):
                text = (addon_root / "service.py").read_text(encoding="utf-8")

                self.assertIn("STARTUP_DELAY_SECONDS = 8", text)
                self.assertNotIn("STARTUP_DELAY_SECONDS = 20", text)

    def test_giptv_entrypoints_do_not_import_asyncio(self):
        for addon_root in [GIPTV_ROOT, SAVED_BUILD_GIPTV_ROOT]:
            with self.subTest(addon_root=str(addon_root)):
                text = (addon_root / "default.py").read_text(encoding="utf-8")

                self.assertNotIn("from asyncio import", text)
                self.assertNotIn("import asyncio", text)

    def test_live_guide_router_modes_are_enabled(self):
        for addon_root in [
            GIPTV_ROOT,
            SAVED_BUILD_GIPTV_ROOT,
            NIKE_REPO_GIPTV_ROOT,
            FAMILY_REPO_GIPTV_ROOT,
        ]:
            with self.subTest(addon_root=str(addon_root)):
                text = (addon_root / "resources" / "lib" / "router.py").read_text(
                    encoding="utf-8"
                )

                self.assertIn('if mode == "live_guide":', text)
                self.assertIn("navigator.list_live_guide(", text)
                self.assertIn('if mode == "live_guide_group":', text)
                self.assertIn("navigator.list_live_guide_group(", text)

        for zip_path in [NIKE_UPLOAD_ZIP, FAMILY_UPLOAD_ZIP]:
            with self.subTest(zip=str(zip_path)):
                with zipfile.ZipFile(zip_path) as zf:
                    text = zf.read(
                        "addons/plugin.video.giptv/resources/lib/router.py"
                    ).decode("utf-8")
                    self.assertIn('if mode == "live_guide_group":', text)
                    self.assertIn("navigator.list_live_guide_group(", text)

    def test_patched_giptv_is_packaged_from_nikeflix_repo(self):
        cases = [
            (
                Path(r"A:\Development\Version Control\Github\repository.NikeFlix"),
                "repository.NikeFlix",
                Path(r"A:\Main User Files\Downloads\KodiBuild\Kodi\userdata\Database\Addons33.db"),
                NIKE_UPLOAD_ZIP,
            ),
            (
                Path(r"A:\Development\Version Control\Github\repository.NikeFlixFamily"),
                "repository.NikeFlixFamily",
                Path(r"C:\Users\tan\AppData\Roaming\Kodi\userdata\Database\Addons33.db"),
                FAMILY_UPLOAD_ZIP,
            ),
        ]

        for repo_root, expected_origin, addons_db, upload_zip in cases:
            with self.subTest(repo=str(repo_root)):
                addon_xml = repo_root / "repo" / "plugin.video.giptv" / "addon.xml"
                self.assertTrue(addon_xml.exists())
                addon = ET.parse(addon_xml).getroot()
                self.assertEqual(TARGET_GIPTV_VERSION, addon.attrib["version"])
                self.assertTrue(
                    (
                        repo_root
                        / "repo"
                        / "zips"
                        / "plugin.video.giptv"
                        / f"plugin.video.giptv-{TARGET_GIPTV_VERSION}.zip"
                    ).exists()
                )

                with sqlite3.connect(addons_db) as con:
                    installed = con.execute(
                        "select enabled, origin, disabledReason from installed where addonID=?",
                        ("plugin.video.giptv",),
                    ).fetchone()
                self.assertEqual((1, expected_origin, 0), installed)

                with zipfile.ZipFile(upload_zip) as zf:
                    addon_text = zf.read("addons/plugin.video.giptv/addon.xml").decode(
                        "utf-8"
                    )
                    self.assertIn(f'version="{TARGET_GIPTV_VERSION}"', addon_text)

    def test_live_guide_api_supports_unfiltered_stream_fetch(self):
        for addon_root in [GIPTV_ROOT, SAVED_BUILD_GIPTV_ROOT]:
            with self.subTest(addon_root=str(addon_root)):
                api_text = (
                    addon_root / "resources" / "apis" / "xtream_api.py"
                ).read_text(encoding="utf-8")
                navigator_text = (
                    addon_root / "resources" / "lib" / "navigator.py"
                ).read_text(encoding="utf-8")

                self.assertIn("def get_all_live_streams():", api_text)
                self.assertIn("xtream_api.get_all_live_streams()", navigator_text)

    def test_service_defers_api_work_and_avoids_startup_dialogs(self):
        text = (GIPTV_ROOT / "service.py").read_text(encoding="utf-8")

        self.assertIn("STARTUP_DELAY_SECONDS", text)
        self.assertIn("monitor.waitForAbort(STARTUP_DELAY_SECONDS)", text)
        self.assertNotIn("xbmc.sleep(3000)", text)
        self.assertNotIn("xbmcgui.Dialog().ok", text)
        self.assertNotIn("show_changelog()", text)

    def test_service_starts_players_after_startup_delay(self):
        text = (GIPTV_ROOT / "service.py").read_text(encoding="utf-8")

        delay_pos = text.index("monitor.waitForAbort(STARTUP_DELAY_SECONDS)")
        trakt_pos = text.index("player = TraktPlayer()")
        proxy_pos = text.index("proxy_player = ProxyPlayer()")
        api_pos = text.index("ensure_api_ready()")

        self.assertLess(delay_pos, trakt_pos)
        self.assertLess(delay_pos, proxy_pos)
        self.assertLess(delay_pos, api_pos)


if __name__ == "__main__":
    unittest.main()
