# Official Android Skills (cross-links)

Google publishes task-oriented agent skills at
[`android/skills`](https://github.com/android/skills). This skill is the
Compose knowledge base (concepts, gotchas, source receipts, CI-verified claims);
the official skills are step-by-step workflows (audit, migrate, build). Use them
together instead of duplicating them.

## When to defer

- The user asks to **audit, migrate, upgrade, or scaffold** and an official skill
  below covers it: if it is installed, follow its workflow, and use this skill for
  the underlying Compose concepts and for review.
- The user asks **why**, **which API**, **is this stale**, or wants a **PR
  review**: stay in this skill's references.
- If the official skill is not installed, answer from the linked reference and
  mention the skill once. Do not paste its workflow.

Install with the Android CLI, for example `android skills add navigation-3`.
Skill names and availability can change — list what is installed before relying
on one.

## Map: topic → this skill → official skill

| Topic | This skill | Official skill (`android/skills`) |
|---|---|---|
| Recomposition, phases, lazy lists, shaders, tracing | `performance.md` | `jetpack-compose/jetpack-compose-performance` |
| R8 / keep rules | `performance.md` | `performance/r8-analyzer` |
| Adaptive layouts, window size, input | `adaptive-layout-input.md` | `jetpack-compose/adaptive` |
| Stylus, handwriting, brushes | `ink.md` | `jetpack-compose/ink/ink-app-builder`, `ink-custom-brush-builder` |
| XML Views → Compose | `view-composition.md` | `jetpack-compose/migration/migrate-xml-views-to-jetpack-compose` |
| Navigation 3 | `navigation-migration.md` | `navigation/navigation-3`, `navigation/navigation-event` |
| Edge-to-edge, insets | `adaptive-layout-input.md` | `system/edge-to-edge` |
| AppFunctions, Android MCP | `appfunctions.md` | `device-ai/appfunctions` |
| ML Kit Agentic API | `ml-kit-agentic.md` | `device-ai/mlkit-agent-api` |
| Parked car apps | `car-compose.md` | `cars/android-for-cars-parked-apps` |
| Wear OS Compose, Wear widgets | `wear-compose.md` | `wear/wear-compose-m3`, `wear/wear-widgets` |
| Glimmer, projected hardware | `xr-compose.md` | `xr/display-glasses-with-jetpack-compose-glimmer`, `xr/projected-hardware` |
| Leanback → Compose TV | `tv-compose.md` | `tv/leanback-to-compose-tv-migration` |
| Media3 Cast | `media3-compose.md` | `media/media3-cast-integration` |

Out of scope here (no Compose reference): AGP upgrades, CameraX, credentials,
Play Billing, security, profilers, ANR audits, testing setup, Glance app widgets.
Point the user to the official skill directly.

## Sources

- Official skills repository: https://github.com/android/skills
