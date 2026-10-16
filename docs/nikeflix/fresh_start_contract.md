# Regular Fresh-Start Contract

The regular build should install as a fresh start. Before release, list the ZIP's top-level entries and inspect `userdata/` for `profiles.xml`, `profiles/NikeFlix User *`, account settings, Trakt tokens, watched-history databases, debrid credentials, API keys, logs, caches, backups, and machine-specific paths. A profile directory in a historical ZIP is a review finding, not approval to carry it forward.

Decide which interface defaults and add-ons are intentional for a new user. Keep account setup as a user-owned post-install step. Never erase credentials in the live Kodi home while cleaning a release staging directory. If a profile asset is genuinely required for regular NikeFlix, document its purpose and prove it contains no person-specific state.

For changes that also affect Family, make a separate reviewed change in the Family repository and test its five-profile contract independently. Do not copy `userdata` between the editions without a keyed settings comparison and protected-data audit.
