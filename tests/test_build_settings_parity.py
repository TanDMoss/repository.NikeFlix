import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


LIVE_BUILD = Path(r"C:\Users\tan\AppData\Roaming\Kodi")
SAVED_BUILD = Path(r"A:\Main User Files\Downloads\KodiBuild\Kodi")

CORE_ADDONS = [
    "skin.titan.bingie.mod",
    "plugin.video.themoviedb.helper",
    "plugin.video.umbrella",
    "plugin.video.fenlight",
    "plugin.video.giptv",
    "service.subtitles.a4ksubtitles",
    "script.module.resolveurl",
]


def profile_roots(kodi_root):
    roots = [kodi_root / "userdata"]
    profiles = kodi_root / "userdata" / "profiles"
    if profiles.exists():
        roots.extend(
            path
            for path in sorted(profiles.iterdir())
            if path.is_dir() and path.name != "userpicture"
        )
    return roots


def profile_names(kodi_root):
    root = ET.parse(kodi_root / "userdata" / "profiles.xml").getroot()
    return [node.findtext("name", "") for node in root.findall("profile")]


def setting_map(path):
    root = ET.parse(path).getroot()
    values = {}
    for setting in root.findall(".//setting"):
        setting_id = setting.attrib.get("id")
        if not setting_id or "trakt" in setting_id.lower():
            continue
        values[setting_id] = setting.text or ""
    return values


class BuildSettingsParityTests(unittest.TestCase):
    def test_both_builds_have_five_login_profiles(self):
        for kodi_root in (LIVE_BUILD, SAVED_BUILD):
            with self.subTest(kodi=str(kodi_root)):
                root = ET.parse(kodi_root / "userdata" / "profiles.xml").getroot()
                self.assertEqual("true", root.findtext("useloginscreen"))
                self.assertEqual("-1", root.findtext("autologin"))
                self.assertEqual(5, len(root.findall("profile")))

                for profile_dir in [
                    kodi_root / "userdata",
                    *[
                        kodi_root / "userdata" / "profiles" / f"NikeFlix User {index}"
                        for index in range(2, 6)
                    ],
                ]:
                    self.assertTrue((profile_dir / "addon_data" / "skin.titan.bingie.mod" / "settings.xml").exists())
                    self.assertTrue((profile_dir / "guisettings.xml").exists())

    def test_core_addon_settings_match_between_builds_except_trakt(self):
        live_profiles = profile_roots(LIVE_BUILD)
        saved_profiles = profile_roots(SAVED_BUILD)
        self.assertEqual(5, len(live_profiles))
        self.assertEqual(5, len(saved_profiles))

        for live_profile, saved_profile in zip(live_profiles, saved_profiles):
            for addon_id in CORE_ADDONS:
                live_settings = live_profile / "addon_data" / addon_id / "settings.xml"
                saved_settings = saved_profile / "addon_data" / addon_id / "settings.xml"
                if not live_settings.exists() or not saved_settings.exists():
                    continue

                with self.subTest(profile=saved_profile.name, addon=addon_id):
                    self.assertEqual(setting_map(live_settings), setting_map(saved_settings))


if __name__ == "__main__":
    unittest.main()
