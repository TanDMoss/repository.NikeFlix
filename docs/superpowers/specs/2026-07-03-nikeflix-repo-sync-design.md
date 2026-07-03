# NikeFlix Repository Sync And Upstream Update Design

## Goal

Bring `repository.NikeFlixFamily` into structural alignment with `repository.NikeFlix`, while ignoring the custom add-ons `plugin.program.nikeflixwizard`, `plugin.program.nikeflixfamilywizard`, and `skin.titan.bingie.mod` for update decisions. After alignment, update packaged add-ons in both repositories to the latest upstream versions where the upstream source is identifiable and version comparison is reliable.

## Scope Rules

- `repository.NikeFlix` is the canonical add-on set.
- Any add-on directory present in `repository.NikeFlixFamily/repo` but not present in `repository.NikeFlix/repo` must be removed.
- The custom add-ons `plugin.program.nikeflixwizard`, `plugin.program.nikeflixfamilywizard`, and `skin.titan.bingie.mod` are excluded from version-update decisions.
- Add-ons with unclear or unverifiable upstream sources are not updated automatically, but they are still removed from `repository.NikeFlixFamily` if they violate the canonical directory-set rule.

## Canonical Set

The canonical directory set is the set of add-on directories under `A:\Development\Version Control\Github\repository.NikeFlix\repo`, excluding `zips`.

`repository.NikeFlixFamily` must end with the same directory set as `repository.NikeFlix`, except for its own repository add-on and family wizard naming differences:

- `repository.NikeFlix` vs `repository.NikeFlixFamily`
- `plugin.program.nikeflixwizard` vs `plugin.program.nikeflixfamilywizard`

Everything else must match by directory presence.

## Update Strategy

### 1. Structural Sync

- Enumerate add-on directories in both repositories.
- Remove extra directories from `repository.NikeFlixFamily/repo` that do not exist in `repository.NikeFlix/repo`.
- Preserve directories that exist in both repos, even if their contents differ.

Expected removals from `repository.NikeFlixFamily` based on the current audit:

- `context.seren`
- `plugin.video.seren`
- `script.skin.helper 2.colorpicker`
- `script.skin.helper 2.service`

### 2. Upstream Version Updates

For each add-on in scope:

- Resolve its original upstream source from one of:
  - git submodule origin
  - `.gitmodules`
  - `<source>` in `addon.xml`
  - `<website>` or raw GitHub repo URLs in repository metadata
- Fetch the upstream `addon.xml` where possible.
- Compare the local packaged version to the upstream version.
- If upstream is newer, replace the local add-on contents with the upstream version using the existing local source model:
  - update submodule-backed directories from their upstream git source
  - refresh copied directories from their upstream repository content

### 3. Non-Automatic Cases

Do not auto-update these unless a reliable upstream manifest is found during execution:

- `plugin.program.nikeflixwizard`
- `plugin.program.nikeflixfamilywizard`
- `skin.titan.bingie.mod`
- add-ons whose source mapping remains unresolved

## Current Known Upstream-Newer Add-ons

### `repository.NikeFlix`

- `plugin.video.themoviedb.helper` `6.15.2` -> `6.15.8`
- `plugin.video.youtube` `7.4.3+beta.1` -> `7.4.4`
- `repository.G00380316` `2.9.1` -> `3.0.3`
- `script.module.jurialmunkey` `0.2.33` -> `0.2.35`
- `script.skinshortcuts` `2.1.0` -> `3.0.2~beta3`
- `script.skinvariables` `2.1.35` -> `2.2.2`

### `repository.NikeFlixFamily`

In addition to matching the NikeFlix updates, the current audit shows these stale copies:

- `context.themoviedb.helper` `1.1.1` -> `2.0.0`
- `plugin.video.themoviedb.helper` `6.11.5` -> `6.15.8`
- `plugin.video.youtube` `7.1.1.1` -> `7.4.4`
- `repository.G00380316` `1.2.2` -> `3.0.3`
- `repository.bugatsinho` `2.7` -> `2.8`
- `resource.font.robotocjksc` `0.0.1` -> `0.0.3`
- `script.module.jurialmunkey` `0.2.29` -> `0.2.35`
- `script.skin.helper.colorpicker` `2.0.2` -> `2.0.3`
- `script.skin.helper.service` `1.2.0` -> `1.20.1`
- `script.skinshortcuts` `2.1.0` -> `3.0.2~beta3`
- `script.skinvariables` `1.1.1` -> `2.2.2`
- `script.texturemaker` `0.2.8` -> `0.2.11`
- `script.tv.show.next.aired` `8.0.3` -> `8.0.4`

Some of those will disappear from Family if the add-on itself is removed by the structural sync rule.

## Data Flow

1. Read directory sets from both repository roots.
2. Compute Family-only extras and remove them.
3. Resolve upstream source per add-on.
4. Fetch upstream version metadata.
5. Update local add-on contents when upstream is newer.
6. Regenerate repository metadata and zip outputs using the repository’s existing generation scripts.
7. Verify:
   - Family directory set matches NikeFlix by rule.
   - updated `addon.xml` versions match expected upstream versions.
   - generated `zips` and repository manifests are refreshed.

## Error Handling

- If an upstream source cannot be resolved or fetched, log it as unverified and leave the add-on unchanged.
- If an update script or packaging step fails for one add-on, continue collecting the rest of the result set and report the partial failure explicitly.
- If a directory removal would affect a custom excluded add-on, stop and re-check the rule rather than deleting it.

## Verification

Verification after implementation must include:

- directory diff between both `repo` folders after exclusions
- version spot-checks for all updated add-ons
- regenerated package artifacts present in both repositories
- summary of:
  - removed Family-only add-ons
  - updated add-ons
  - unresolved add-ons with unknown upstreams

## Risks

- Some copied add-ons do not expose a reliable upstream repo layout, so automatic refresh may need to fall back to manual review.
- Several add-ons in the repositories appear locally newer than the public source currently resolved; those should not be downgraded.
- Repo generation may depend on local scripts assuming specific folder contents, so structural removals should happen before packaging verification.
