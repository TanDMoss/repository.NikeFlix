# Regular NikeFlix Repository Guide

This repository owns the regular NikeFlix repository add-on and wizard. Regular NikeFlix is intended as a fresh-start build. Read `docs/nikeflix/INDEX.md` before changing add-ons, wizard feeds, generated repository files, or the build ZIP. Read the nearest more-specific `AGENTS.md` if one is later added.

## Connected locations

- This checkout: `A:\Development\Version Control\Github\repository.NikeFlix`.
- GitHub: `https://github.com/TanDMoss/repository.NikeFlix`.
- Family checkout: `A:\Development\Version Control\Github\repository.NikeFlixFamily`, GitHub: `https://github.com/TanDMoss/repository.NikeFlixFamily`.
- Live Kodi: `C:\Users\tan\AppData\Roaming\Kodi`.
- NikeFlix prompt and knowledge space: `A:\Productivity\Notes\Obsidian\Vaults\Tech Vault\Tech Vault\Chosen-Agents\NikeFlix`.

These are separate authorities. GitHub and this checkout own source; the Kodi home is runtime state; the build-feed URL and downloaded archive are publication state. A local version label is not proof that the published ZIP matches it.

## Edition and data boundaries

The regular wizard ID is `plugin.program.nikeflixwizard`; repository add-on ID is `repository.NikeFlix`. Keep this edition a fresh start. Inspect any candidate archive for inherited Family profile folders, account tokens, watched data, databases, caches, logs, and backups. Do not import live Kodi `userdata` or credentials wholesale. Keep TMDb Helper enabled when repairing its behaviour unless Tanner explicitly changes that requirement.

## Work sequence

1. Read `docs/nikeflix/INDEX.md`, inspect `git status`, branch, and remote before editing. Preserve unrelated worktree changes.
2. Locate source under `repo/`, wizard feed at `repo/plugin.program.nikeflixwizard/resources/text/builds.txt`, generated index/checksum under `repo/zips/`, and the intended build ZIP.
3. Back up any live Kodi data before touching it; stop Kodi for live-file edits. Stage ZIP extraction under the Kodi home and inspect top-level `addons/`, `media/`, `userdata/` before applying anything.
4. Inspect `repo_generator.py`, `update_versions.py`, and `update_and_generate.py` before running them. The generator rewrites repository artifacts; `update_and_generate.py` can remove `repo/zips`. Run only when that mutation is the task.
5. Run focused tests from `tests/` and validate XML, ZIP entries, generated index/checksum, feed version and URL. Verify GitHub publication and the served build ZIP separately from Kodi runtime.

Do not claim completion at a passing local test or generated ZIP. Record which of source, tests, GitHub, published archive, and clean Kodi runtime was actually proven. Use a targeted regression test or exact non-automatable proof boundary for a confirmed bug fix.
