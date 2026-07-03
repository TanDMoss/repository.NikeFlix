import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


NIKE_REPO = Path(r"A:\Development\Version Control\Github\repository.NikeFlix")
FAMILY_REPO = Path(r"A:\Development\Version Control\Github\repository.NikeFlixFamily")

EXPECTED_FAMILY_REMOVALS = {
    "context.seren",
    "plugin.video.seren",
    "script.skin.helper 2.colorpicker",
    "script.skin.helper 2.service",
}
EXPECTED_SHARED_VERSIONS = {
    "context.themoviedb.helper": "2.0.0",
    "plugin.video.themoviedb.helper": "6.15.8",
    "plugin.video.youtube": "7.4.4",
    "repository.G00380316": "3.0.3",
    "repository.bugatsinho": "2.8",
    "resource.font.robotocjksc": "0.0.3",
    "script.module.jurialmunkey": "0.2.35",
    "script.skin.helper.colorpicker": "2.0.3",
    "script.skin.helper.service": "1.20.1",
    "script.skinshortcuts": "3.0.2~beta3",
    "script.skinvariables": "2.2.2",
    "script.texturemaker": "0.2.11",
    "script.tv.show.next.aired": "8.0.4",
}
EXPECTED_REPO_VERSION = "3.3.0"


def addon_dirs(repo_root):
    repo_dir = repo_root / "repo"
    return sorted(
        path.name
        for path in repo_dir.iterdir()
        if path.is_dir() and path.name != "zips"
    )


def addon_version(repo_root, addon_id):
    root = ET.parse(repo_root / "repo" / addon_id / "addon.xml").getroot()
    return root.attrib["version"]


class RepoSyncAlignmentTests(unittest.TestCase):
    def test_family_has_no_extra_addons_after_sync(self):
        nike = set(addon_dirs(NIKE_REPO))
        family = set(addon_dirs(FAMILY_REPO))

        nike_normalized = (nike - {"repository.NikeFlix", "plugin.program.nikeflixwizard"}) | {
            "repository.NikeFlixFamily",
            "plugin.program.nikeflixfamilywizard",
        }
        extras = family - nike_normalized

        self.assertEqual(set(), extras)
        for addon_id in EXPECTED_FAMILY_REMOVALS:
            self.assertFalse((FAMILY_REPO / "repo" / addon_id).exists(), addon_id)

    def test_shared_versions_match_expected_matrix(self):
        for addon_id, expected in EXPECTED_SHARED_VERSIONS.items():
            with self.subTest(repo="nike", addon=addon_id):
                self.assertEqual(expected, addon_version(NIKE_REPO, addon_id))
            with self.subTest(repo="family", addon=addon_id):
                self.assertEqual(expected, addon_version(FAMILY_REPO, addon_id))

    def test_repository_versions_and_root_links_are_in_lockstep(self):
        cases = [
            (NIKE_REPO, "repository.NikeFlix", r"repository\.NikeFlix-(\d+\.\d+\.\d+)\.zip"),
            (FAMILY_REPO, "repository.NikeFlixFamily", r"repository\.NikeFlixFamily-(\d+\.\d+\.\d+)\.zip"),
        ]

        for repo_root, repo_id, pattern in cases:
            with self.subTest(repo=str(repo_root)):
                repo_version = addon_version(repo_root, repo_id)
                self.assertEqual(EXPECTED_REPO_VERSION, repo_version)

                html = (repo_root / "index.html").read_text(encoding="utf-8")
                match = re.search(pattern, html)
                self.assertIsNotNone(match)
                self.assertEqual(repo_version, match.group(1))
                self.assertTrue(
                    (repo_root / f"{repo_id}-{repo_version}.zip").exists(),
                    repo_root / f"{repo_id}-{repo_version}.zip",
                )
                self.assertTrue(
                    (repo_root / "repo" / "zips" / repo_id / f"{repo_id}-{repo_version}.zip").exists()
                )


if __name__ == "__main__":
    unittest.main()
