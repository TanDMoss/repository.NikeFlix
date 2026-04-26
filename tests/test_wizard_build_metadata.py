import re
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NIKE_REPO = Path(r"A:\Development\Version Control\Github\repository.NikeFlix")
FAMILY_REPO = Path(r"A:\Development\Version Control\Github\repository.NikeFlixFamily")
OUTPUT_DIR = Path(r"A:\Main User Files\Downloads\Kodi Builds")

TARGET_BUILD_VERSION = "3.2.6"
TARGET_SKIN_VERSION = "2.2.8"
EXPECTED_WIZARD_IMPORTS = {
    "xbmc.python": "3.0.0",
    "script.module.requests": "",
    "script.module.six": "",
    "script.kodi.android.update": "1.1.7",
    "script.speedtester": "1.1.2",
}
EXPECTED_SKIN_IMPORTS = {
    "xbmc.gui": "5.17.0",
    "script.bingie.helper": "1.1.2",
    "script.skinshortcuts": "2.1.0",
    "script.skin.helper.service": "1.30.0",
    "script.skin.helper.widgets": "1.30.0",
    "script.skin.helper.backgrounds": "1.0.36",
    "resource.images.skinbackgrounds.titanium": "1.0.0",
    "resource.images.skinicons.wide": "1.0.5",
    "resource.images.backgroundoverlays.basic": "1.0.0",
    "resource.images.studios.coloured": "0.0.23",
    "plugin.video.themoviedb.helper": "5.2.12",
    "plugin.program.autocompletion": "2.1.2",
    "plugin.video.youtube": "7.0.2.2",
}
REMOVED_ADDONS = {
    "plugin.program.autowidget",
    "repository.thecrew",
    "script.skin.helper.skinbackup",
}
REMOVED_BUILD_ADDONS = REMOVED_ADDONS | {
    "plugin.program.NikeFlix",
    "plugin.video.giptv.codex-bak-20260424-083019",
    "plugin.video.madtitansports",
    "plugin.video.sporthdme",
    "plugin.video.thecrew",
    "plugin.video.tvone112",
    "script.module.thecrew",
    "script.thecrew.artwork",
}


def addon_attrs(path):
    root = ET.parse(path).getroot()
    return root.attrib


def addon_import_versions(path):
    root = ET.parse(path).getroot()
    return {
        import_node.attrib["addon"]: import_node.attrib.get("version", "")
        for import_node in root.findall("./requires/import")
    }


def indexed_addon_import_versions(path, addon_id):
    root = ET.parse(path).getroot()
    addon = root.find(f"./addon[@id='{addon_id}']")
    if addon is None:
        raise AssertionError(f"missing {addon_id} in {path}")
    return {
        import_node.attrib["addon"]: import_node.attrib.get("version", "")
        for import_node in addon.findall("./requires/import")
    }


def read_builds(path):
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r'([^=]+)="(.*)"', line.strip())
        if match:
            values[match.group(1)] = match.group(2)
    return values


def setting_defaults(path):
    root = ET.parse(path).getroot()
    return {
        setting.attrib["id"]: setting.attrib.get("default", "")
        for setting in root.findall(".//setting")
        if "id" in setting.attrib
    }


class WizardBuildMetadataTests(unittest.TestCase):
    def test_repo_wizard_build_and_skin_versions_are_current(self):
        cases = [
            (
                NIKE_REPO,
                "repository.NikeFlix",
                "plugin.program.nikeflixwizard",
                "plugin.program.nikeflixwizard",
            ),
            (
                FAMILY_REPO,
                "repository.NikeFlixFamily",
                "plugin.program.nikeflixfamilywizard",
                "plugin.program.NikeFlixFamilyWizard",
            ),
        ]

        for repo_root, repo_id, wizard_folder, wizard_id in cases:
            with self.subTest(repo=str(repo_root)):
                repo_addon = addon_attrs(repo_root / "repo" / repo_id / "addon.xml")
                wizard_addon = addon_attrs(repo_root / "repo" / wizard_folder / "addon.xml")
                skin_addon = addon_attrs(repo_root / "repo" / "skin.titan.bingie.mod" / "addon.xml")
                zip_skin_addon = addon_attrs(repo_root / "repo" / "zips" / "skin.titan.bingie.mod" / "addon.xml")
                builds = read_builds(repo_root / "repo" / wizard_folder / "resources" / "text" / "builds.txt")

                self.assertEqual(TARGET_BUILD_VERSION, repo_addon["version"])
                self.assertEqual(wizard_id, wizard_addon["id"])
                self.assertEqual(TARGET_BUILD_VERSION, wizard_addon["version"])
                self.assertEqual(wizard_id, builds["id"])
                self.assertEqual(TARGET_BUILD_VERSION, builds["version"])
                self.assertEqual(TARGET_SKIN_VERSION, skin_addon["version"])
                self.assertEqual(TARGET_SKIN_VERSION, zip_skin_addon["version"])
                self.assertTrue(
                    (repo_root / "repo" / "zips" / "skin.titan.bingie.mod" / f"skin.titan.bingie.mod-{TARGET_SKIN_VERSION}.zip").exists()
                )
                with zipfile.ZipFile(
                    repo_root / "repo" / "zips" / wizard_id / f"{wizard_id}-{TARGET_BUILD_VERSION}.zip"
                ) as zf:
                    self.assertIn(f"{wizard_id}/addon.xml", set(zf.namelist()))

    def test_repo_and_wizard_metadata_keep_xml_and_runtime_dependency_versions(self):
        cases = [
            (
                NIKE_REPO,
                "repository.NikeFlix",
                "plugin.program.nikeflixwizard",
                "plugin.program.nikeflixwizard",
            ),
            (
                FAMILY_REPO,
                "repository.NikeFlixFamily",
                "plugin.program.nikeflixfamilywizard",
                "plugin.program.NikeFlixFamilyWizard",
            ),
        ]

        for repo_root, repo_id, wizard_folder, wizard_id in cases:
            paths = [
                repo_root / "repo" / repo_id / "addon.xml",
                repo_root / "repo" / "zips" / repo_id / "addon.xml",
                repo_root / "repo" / wizard_folder / "addon.xml",
                repo_root / "repo" / "zips" / wizard_id / "addon.xml",
            ]
            for path in paths:
                with self.subTest(path=str(path)):
                    self.assertTrue(path.read_text(encoding="utf-8").startswith('<?xml version="1.0"'), path)

            for path in [
                repo_root / "repo" / wizard_folder / "addon.xml",
                repo_root / "repo" / "zips" / wizard_id / "addon.xml",
            ]:
                with self.subTest(wizard=str(path)):
                    self.assertEqual(EXPECTED_WIZARD_IMPORTS, addon_import_versions(path))

            for path in [
                repo_root / "repo" / "zips" / "addons.xml",
            ]:
                with self.subTest(index=str(path), wizard=wizard_id):
                    self.assertEqual(EXPECTED_WIZARD_IMPORTS, indexed_addon_import_versions(path, wizard_id))

    def test_titan_bingie_keeps_kodi_omega_dependency_versions(self):
        paths = [
            NIKE_REPO / "repo" / "skin.titan.bingie.mod" / "addon.xml",
            NIKE_REPO / "repo" / "zips" / "skin.titan.bingie.mod" / "addon.xml",
            FAMILY_REPO / "repo" / "skin.titan.bingie.mod" / "addon.xml",
            FAMILY_REPO / "repo" / "zips" / "skin.titan.bingie.mod" / "addon.xml",
            Path(r"C:\Users\tan\AppData\Roaming\Kodi\addons\skin.titan.bingie.mod\addon.xml"),
            Path(r"A:\Main User Files\Downloads\KodiBuild\Kodi\addons\skin.titan.bingie.mod\addon.xml"),
        ]

        for path in paths:
            with self.subTest(path=str(path)):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith('<?xml version="1.0"'), path)
                self.assertEqual(TARGET_SKIN_VERSION, addon_attrs(path)["version"])
                self.assertEqual(EXPECTED_SKIN_IMPORTS, addon_import_versions(path))

        for path in [
            NIKE_REPO / "repo" / "zips" / "addons.xml",
            FAMILY_REPO / "repo" / "zips" / "addons.xml",
        ]:
            with self.subTest(index=str(path)):
                self.assertEqual(
                    EXPECTED_SKIN_IMPORTS,
                    indexed_addon_import_versions(path, "skin.titan.bingie.mod"),
                )

    def test_family_wizard_runtime_config_points_to_family_repo(self):
        uservar = (FAMILY_REPO / "repo" / "plugin.program.nikeflixfamilywizard" / "uservar.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("ADDONTITLE = 'nikeflixfamilywizard'", uservar)
        self.assertIn("BUILDERNAME = 'nikeflixfamilywizard'", uservar)
        self.assertIn("REPOID = 'repository.NikeFlixFamily'", uservar)
        self.assertIn("repository.NikeFlixFamily", uservar)

    def test_wizard_defaults_keep_existing_profiles_and_gui_settings(self):
        for path in [
            NIKE_REPO / "repo" / "plugin.program.nikeflixwizard" / "resources" / "settings.xml",
            FAMILY_REPO / "repo" / "plugin.program.nikeflixfamilywizard" / "resources" / "settings.xml",
        ]:
            with self.subTest(path=str(path)):
                defaults = setting_defaults(path)
                self.assertEqual("true", defaults["keepprofiles"])
                self.assertEqual("true", defaults["keepguisettings"])

    def test_extract_only_skips_profiles_that_already_exist(self):
        for path in [
            NIKE_REPO / "repo" / "plugin.program.nikeflixwizard" / "resources" / "libs" / "extract.py",
            FAMILY_REPO / "repo" / "plugin.program.nikeflixfamilywizard" / "resources" / "libs" / "extract.py",
        ]:
            with self.subTest(path=str(path)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("def _target_exists_for_zip_entry", text)
                self.assertIn("_target_exists_for_zip_entry(filename, _out)", text)
                self.assertNotIn("elif _is_profile_zip_entry(file) and CONFIG.KEEPPROFILES == 'true':\n            skip = True", text)

    def test_removed_addons_are_not_in_repos_or_build_folders(self):
        for repo_root in (NIKE_REPO, FAMILY_REPO):
            for addon_id in REMOVED_ADDONS:
                with self.subTest(repo=str(repo_root), addon=addon_id):
                    self.assertFalse((repo_root / "repo" / addon_id).exists())
                    self.assertFalse((repo_root / "repo" / "zips" / addon_id).exists())

        for kodi_root in (Path(r"C:\Users\tan\AppData\Roaming\Kodi"), Path(r"A:\Main User Files\Downloads\KodiBuild\Kodi")):
            for addon_id in REMOVED_BUILD_ADDONS:
                with self.subTest(kodi=str(kodi_root), addon=addon_id):
                    self.assertFalse((kodi_root / "addons" / addon_id).exists())
                    self.assertFalse((kodi_root / "userdata" / "addon_data" / addon_id).exists())

    def test_missing_optional_wizard_login_addons_are_not_error_level(self):
        for path in [
            NIKE_REPO / "repo" / "plugin.program.nikeflixwizard" / "resources" / "libs" / "loginit.py",
            NIKE_REPO / "repo" / "plugin.program.nikeflixwizard" / "resources" / "libs" / "traktit.py",
            FAMILY_REPO / "repo" / "plugin.program.nikeflixfamilywizard" / "resources" / "libs" / "loginit.py",
            FAMILY_REPO / "repo" / "plugin.program.nikeflixfamilywizard" / "resources" / "libs" / "traktit.py",
        ]:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path)):
                self.assertNotRegex(text, r"is not installed'.*level=xbmc\.LOGERROR")

    def test_upload_zips_include_profiles_and_core_settings(self):
        expected = {
            "nikeflixwizard.zip": "plugin.program.nikeflixwizard",
            "nikeflixfamilywizard.zip": "plugin.program.NikeFlixFamilyWizard",
        }

        for filename, wizard_id in expected.items():
            with self.subTest(zip=filename):
                zip_path = OUTPUT_DIR / filename
                self.assertTrue(zip_path.exists(), str(zip_path))
                with zipfile.ZipFile(zip_path) as zf:
                    names = set(zf.namelist())
                    self.assertIn("userdata/profiles.xml", names)
                    for profile in range(2, 6):
                        self.assertIn(f"userdata/profiles/NikeFlix User {profile}/guisettings.xml", names)
                    self.assertIn("addons/skin.titan.bingie.mod/addon.xml", names)
                    self.assertIn(f"addons/{wizard_id}/addon.xml", names)
                    for addon_id in REMOVED_BUILD_ADDONS:
                        self.assertFalse(any(name.startswith(f"addons/{addon_id}/") for name in names), addon_id)
                        self.assertFalse(
                            any(name.startswith(f"userdata/addon_data/{addon_id}/") for name in names),
                            addon_id,
                        )

                    skin_xml = zf.read("addons/skin.titan.bingie.mod/addon.xml").decode("utf-8")
                    wizard_xml = zf.read(f"addons/{wizard_id}/addon.xml").decode("utf-8")
                    self.assertTrue(skin_xml.startswith('<?xml version="1.0"'))
                    self.assertTrue(wizard_xml.startswith('<?xml version="1.0"'))
                    self.assertIn(f'version="{TARGET_SKIN_VERSION}"', skin_xml)
                    for addon_id, version in EXPECTED_SKIN_IMPORTS.items():
                        self.assertIn(f'addon="{addon_id}"', skin_xml)
                        self.assertIn(f'version="{version}"', skin_xml)
                    self.assertIn(f'version="{TARGET_BUILD_VERSION}"', wizard_xml)
                    for addon_id, version in EXPECTED_WIZARD_IMPORTS.items():
                        self.assertIn(f'addon="{addon_id}"', wizard_xml)
                        if version:
                            self.assertIn(f'version="{version}"', wizard_xml)


if __name__ == "__main__":
    unittest.main()
