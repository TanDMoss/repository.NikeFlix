# NikeFlix Repository Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `repository.NikeFlixFamily` to the canonical `repository.NikeFlix` add-on set, update the stale shared add-ons to the latest verified upstream versions, and regenerate both repositories as version `3.3.0` so Kodi sees the refresh.

**Architecture:** Treat `A:\Development\Version Control\Github\repository.NikeFlix\repo` as the canonical content source. First add a cross-repo verification test in `repository.NikeFlix`, then refresh the stale NikeFlix add-ons from their upstream sources, mirror the shared add-ons into Family while deleting Family-only extras, bump both repository add-on versions to `3.3.0`, and regenerate `repo\zips` plus the root downloadable zip links by driving the existing `Update-NikeFlix.bat` and `Update-NikeFlix-Build.bat` scripts in each repository.

**Tech Stack:** PowerShell, Git, Python 3, `unittest`, the existing `repo_generator.py` packaging script in each repository

---

## File Structure

- Create: `A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\plugin.video.themoviedb.helper\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\plugin.video.youtube\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\repository.G00380316\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\script.module.jurialmunkey\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\script.skinshortcuts\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\script.skinvariables\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\repository.NikeFlix\addon.xml`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\index.html`
- Modify: shared add-on folders under `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\context.seren`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\plugin.video.seren`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\script.skin.helper 2.colorpicker`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\script.skin.helper 2.service`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\repository.NikeFlixFamily\addon.xml`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlixFamily\index.html`
- Regenerate: `A:\Development\Version Control\Github\repository.NikeFlix\repo\zips\**`
- Regenerate: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\zips\**`
- Replace: root download zips in both repository roots

## Expected Final Shared Versions

These versions should match in both repos after the sync unless the add-on is one of the user-excluded custom packages:

- `context.themoviedb.helper`: `2.0.0`
- `plugin.video.themoviedb.helper`: `6.15.8`
- `plugin.video.youtube`: `7.4.4`
- `repository.G00380316`: `3.0.3`
- `repository.bugatsinho`: `2.8`
- `resource.font.robotocjksc`: `0.0.3`
- `script.module.jurialmunkey`: `0.2.35`
- `script.skin.helper.colorpicker`: `2.0.3`
- `script.skin.helper.service`: `1.20.1`
- `script.skinshortcuts`: `3.0.2~beta3`
- `script.skinvariables`: `2.2.2`
- `script.texturemaker`: `0.2.11`
- `script.tv.show.next.aired`: `8.0.4`

## Explicit No-Touch List

Do not auto-update or remove these during the sync unless the user later changes scope:

- `plugin.program.nikeflixwizard`
- `plugin.program.nikeflixfamilywizard`
- `skin.titan.bingie.mod`

### Task 1: Add Cross-Repo Verification Coverage

**Files:**
- Create: `A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py`
- Test: `A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py`

- [ ] **Step 1: Write the failing test file**

```python
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


NIKE_REPO = Path(r"A:\Development\Version Control\Github\repository.NikeFlix")
FAMILY_REPO = Path(r"A:\Development\Version Control\Github\repository.NikeFlixFamily")

CUSTOM_IDS = {
    "plugin.program.nikeflixwizard",
    "plugin.program.nikeflixfamilywizard",
    "skin.titan.bingie.mod",
}
ALIAS_IDS = {
    ("repository.NikeFlix", "repository.NikeFlixFamily"),
    ("plugin.program.nikeflixwizard", "plugin.program.nikeflixfamilywizard"),
}
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
```

- [ ] **Step 2: Run the new test to verify it fails**

Run:

```bash
python -m unittest A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py -v
```

Expected: FAIL on the Family extra-directory assertion, stale shared version assertions, and the root zip link mismatch because both `index.html` files still point at `3.2.6` while the repository add-ons are already at `3.2.7`.

- [ ] **Step 3: Commit the failing-spec harness**

```bash
git -C "A:\Development\Version Control\Github\repository.NikeFlix" add tests/test_repo_sync_alignment.py
git -C "A:\Development\Version Control\Github\repository.NikeFlix" commit -m "test: add repo sync alignment coverage"
```

### Task 2: Refresh Canonical NikeFlix Add-Ons First

**Files:**
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\plugin.video.themoviedb.helper\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\plugin.video.youtube\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\repository.G00380316\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\script.module.jurialmunkey\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\script.skinshortcuts\**`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\script.skinvariables\**`
- Test: `A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py`

- [ ] **Step 1: Pull the submodule-backed add-ons to the verified upstream tags or heads**

Run:

```bash
git -C "A:\Development\Version Control\Github\repository.NikeFlix" submodule update --init --remote --checkout -- \
  repo/plugin.video.themoviedb.helper \
  repo/script.module.jurialmunkey \
  repo/script.skinvariables
```

Expected: the working tree updates these folders so `addon.xml` versions read `6.15.8`, `0.2.35`, and `2.2.2`.

- [ ] **Step 2: Replace the copied add-ons that are still stale in NikeFlix**

Run:

```powershell
$temp = Join-Path $env:TEMP 'nikeflix-upstream-refresh'
Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $temp | Out-Null

git clone --depth 1 --branch 7.4.4 https://github.com/anxdpanic/plugin.video.youtube.git (Join-Path $temp 'plugin.video.youtube')
git clone --depth 1 --branch 3.0.3 https://github.com/G00380316/gflix.git (Join-Path $temp 'gflix')
git clone --depth 1 --branch 3.0.2~beta3 https://github.com/mikesilvo164/script.skinshortcuts.git (Join-Path $temp 'script.skinshortcuts')
```

Then replace the destination folders with the upstream content:

```powershell
$pairs = @(
  @{Source = (Join-Path $temp 'plugin.video.youtube'); Dest = 'A:\Development\Version Control\Github\repository.NikeFlix\repo\plugin.video.youtube'},
  @{Source = (Join-Path $temp 'gflix\repository.G00380316'); Dest = 'A:\Development\Version Control\Github\repository.NikeFlix\repo\repository.G00380316'},
  @{Source = (Join-Path $temp 'script.skinshortcuts'); Dest = 'A:\Development\Version Control\Github\repository.NikeFlix\repo\script.skinshortcuts'}
)
foreach ($pair in $pairs) {
  $resolved = Resolve-Path -LiteralPath $pair.Dest
  Remove-Item -LiteralPath $resolved -Recurse -Force
  Copy-Item -LiteralPath $pair.Source -Destination $resolved -Recurse
}
```

Expected: `plugin.video.youtube`, `repository.G00380316`, and `script.skinshortcuts` now carry the upstream `addon.xml` versions `7.4.4`, `3.0.3`, and `3.0.2~beta3`.

- [ ] **Step 3: Run the Nike-only assertions until they pass**

Run:

```bash
python -m unittest A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py RepoSyncAlignmentTests.test_shared_versions_match_expected_matrix -v
```

Expected: still FAIL for the Family half of the shared-version assertions, but all NikeFlix subtests should now pass.

- [ ] **Step 4: Commit the canonical add-on refresh**

```bash
git -C "A:\Development\Version Control\Github\repository.NikeFlix" add repo/plugin.video.themoviedb.helper repo/plugin.video.youtube repo/repository.G00380316 repo/script.module.jurialmunkey repo/script.skinshortcuts repo/script.skinvariables
git -C "A:\Development\Version Control\Github\repository.NikeFlix" commit -m "build: refresh canonical addon sources"
```

### Task 3: Remove Family-Only Extras And Mirror Shared Content From NikeFlix

**Files:**
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\context.seren`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\plugin.video.seren`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\script.skin.helper 2.colorpicker`
- Delete: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\script.skin.helper 2.service`
- Modify: shared add-on folders under `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\`
- Test: `A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py`

- [ ] **Step 1: Delete the Family-only add-on directories the user explicitly does not want**

Run:

```powershell
$remove = @(
  'A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\context.seren',
  'A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\plugin.video.seren',
  'A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\script.skin.helper 2.colorpicker',
  'A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\script.skin.helper 2.service'
)
foreach ($path in $remove) {
  $resolved = Resolve-Path -LiteralPath $path
  Remove-Item -LiteralPath $resolved -Recurse -Force
}
```

Expected: those four directories no longer exist under `repository.NikeFlixFamily\repo`.

- [ ] **Step 2: Mirror the shared add-on directories from NikeFlix into Family**

Run:

```powershell
$shared = @(
  'context.embuary.info',
  'context.themoviedb.helper',
  'plugin.video.giptv',
  'plugin.video.themoviedb.helper',
  'plugin.video.youtube',
  'repository.a4kSubtitles',
  'repository.bugatsinho',
  'repository.cocoscrapers',
  'repository.G00380316',
  'repository.Magnetic',
  'repository.marcelveldt',
  'repository.siku2',
  'repository.titan.bingie.mod',
  'repository.umbrella',
  'resource.font.robotocjksc',
  'resource.images.backgroundoverlays.basic',
  'resource.images.busyspinners.basic',
  'resource.images.languageflags.colour',
  'resource.images.moviegenreicons.bingie',
  'resource.images.skinbackgrounds.titanium',
  'resource.images.skinicons.wide',
  'screensaver.titan.bingie.mod',
  'script.artwork.beef',
  'script.bingie.helper',
  'script.embuary.info',
  'script.module.arrow',
  'script.module.cherrypy',
  'script.module.infotagger',
  'script.module.jurialmunkey',
  'script.module.metadatautils',
  'script.module.musicbrainz',
  'script.module.pil',
  'script.module.simplecache',
  'script.module.thetvdb',
  'script.module.tmdbhelper',
  'script.skin.helper.backgrounds',
  'script.skin.helper.colorpicker',
  'script.skin.helper.service',
  'script.skin.helper.widgets',
  'script.skinshortcuts',
  'script.skinvariables',
  'script.texturemaker',
  'script.tv.show.next.aired',
  'skin.titan.bingie.mod'
)

foreach ($addon in $shared) {
  $source = Join-Path 'A:\Development\Version Control\Github\repository.NikeFlix\repo' $addon
  $dest = Join-Path 'A:\Development\Version Control\Github\repository.NikeFlixFamily\repo' $addon
  if (Test-Path -LiteralPath $dest) {
    Remove-Item -LiteralPath (Resolve-Path -LiteralPath $dest) -Recurse -Force
  }
  Copy-Item -LiteralPath $source -Destination $dest -Recurse
}
```

Expected: every shared add-on in Family now matches the NikeFlix copy byte-for-byte, while the Family-specific wizard and repository folders remain untouched.

- [ ] **Step 3: Run the Family structure and shared-version assertions**

Run:

```bash
python -m unittest A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py RepoSyncAlignmentTests.test_family_has_no_extra_addons_after_sync RepoSyncAlignmentTests.test_shared_versions_match_expected_matrix -v
```

Expected: PASS for the Family extra-directory check and every shared-version assertion.

- [ ] **Step 4: Commit the Family structural sync**

```bash
git -C "A:\Development\Version Control\Github\repository.NikeFlixFamily" add repo
git -C "A:\Development\Version Control\Github\repository.NikeFlixFamily" commit -m "build: sync family repo to canonical addon set"
```

### Task 4: Bump Both Repository Packages And Regenerate Artifacts

**Files:**
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\repo\repository.NikeFlix\addon.xml`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlix\index.html`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\repository.NikeFlixFamily\addon.xml`
- Modify: `A:\Development\Version Control\Github\repository.NikeFlixFamily\index.html`
- Regenerate: `repo\zips\**` in both repos
- Replace: `repository.NikeFlix-3.3.0.zip`
- Replace: `repository.NikeFlixFamily-3.3.0.zip`

- [ ] **Step 1: Update the repository add-on versions to `3.3.0`**

Apply these edits:

```diff
*** Update File: A:\Development\Version Control\Github\repository.NikeFlix\repo\repository.NikeFlix\addon.xml
-<addon id="repository.NikeFlix" name="NikeFlix" version="3.2.7"
+<addon id="repository.NikeFlix" name="NikeFlix" version="3.3.0"

*** Update File: A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\repository.NikeFlixFamily\addon.xml
-<addon id="repository.NikeFlixFamily" name="NikeFlixFamily" version="3.2.7"
+<addon id="repository.NikeFlixFamily" name="NikeFlixFamily" version="3.3.0"
```

- [ ] **Step 2: Fix the stale root download links so they match the new package version**

Apply these edits:

```diff
*** Update File: A:\Development\Version Control\Github\repository.NikeFlix\index.html
-<a href="repository.NikeFlix-3.2.6.zip">repository.NikeFlix-3.2.6.zip</a>
+<a href="repository.NikeFlix-3.3.0.zip">repository.NikeFlix-3.3.0.zip</a>

*** Update File: A:\Development\Version Control\Github\repository.NikeFlixFamily\index.html
-<a href="repository.NikeFlixFamily-3.2.6.zip">repository.NikeFlixFamily-3.2.6.zip</a>
+<a href="repository.NikeFlixFamily-3.3.0.zip">repository.NikeFlixFamily-3.3.0.zip</a>
```

- [ ] **Step 3: Rebuild both repositories using the existing batch entrypoints**

Run:

```bash
cmd /c "echo 3.3.0| A:\Development\Version Control\Github\repository.NikeFlix\Update-NikeFlix-Build.bat"
cmd /c "echo 3.3.0| A:\Development\Version Control\Github\repository.NikeFlix\Update-NikeFlix.bat"
cmd /c "echo 3.3.0| A:\Development\Version Control\Github\repository.NikeFlixFamily\Update-NikeFlix-Build.bat"
cmd /c "echo 3.3.0| A:\Development\Version Control\Github\repository.NikeFlixFamily\Update-NikeFlix.bat"
```

Then refresh the root download zips:

```powershell
Copy-Item -LiteralPath 'A:\Development\Version Control\Github\repository.NikeFlix\repo\zips\repository.NikeFlix\repository.NikeFlix-3.3.0.zip' -Destination 'A:\Development\Version Control\Github\repository.NikeFlix\repository.NikeFlix-3.3.0.zip' -Force
Copy-Item -LiteralPath 'A:\Development\Version Control\Github\repository.NikeFlixFamily\repo\zips\repository.NikeFlixFamily\repository.NikeFlixFamily-3.3.0.zip' -Destination 'A:\Development\Version Control\Github\repository.NikeFlixFamily\repository.NikeFlixFamily-3.3.0.zip' -Force
```

Expected: each repo has a fresh `repo\zips\addons.xml`, `repo\zips\addons.xml.md5`, per-add-on zip folders, and a root repository zip whose filename matches `index.html`.

- [ ] **Step 4: Run the full verification set**

Run:

```bash
python -m unittest A:\Development\Version Control\Github\repository.NikeFlix\tests\test_repo_sync_alignment.py -v
python -m unittest A:\Development\Version Control\Github\repository.NikeFlix\tests\test_wizard_build_metadata.py -v
```

Expected: PASS. The new sync test should validate directory parity, shared versions, and root zip consistency. The wizard metadata regression test should keep the excluded custom packages intact.

- [ ] **Step 5: Commit the repository metadata and packaging output**

```bash
git -C "A:\Development\Version Control\Github\repository.NikeFlix" add index.html repo/repository.NikeFlix/addon.xml repo/zips repository.NikeFlix-3.3.0.zip
git -C "A:\Development\Version Control\Github\repository.NikeFlix" commit -m "build: publish repo sync refresh"

git -C "A:\Development\Version Control\Github\repository.NikeFlixFamily" add index.html repo/repository.NikeFlixFamily/addon.xml repo/zips repository.NikeFlixFamily-3.3.0.zip
git -C "A:\Development\Version Control\Github\repository.NikeFlixFamily" commit -m "build: publish family repo sync refresh"
```

## Self-Review

- **Spec coverage:** The plan covers the structural sync, upstream refresh for the verified stale NikeFlix add-ons, Family-only deletions, repository version bump, zip regeneration, and verification/reporting.
- **Placeholder scan:** No `TODO`, `TBD`, or "similar to above" placeholders remain.
- **Type consistency:** The same repository roots, add-on ids, final versions, and root package version `3.3.0` are used throughout the plan.
