# Compose for Wear OS

## Architecture and code sharing

Share domain/data code with the phone app, but keep Wear navigation, density,
interaction, and lifecycle decisions explicit. Dependency injection and
manifests often differ even when feature modules are shared.

Add tests that compare expected multibinding/feature sets across phone and Wear
applications so a manifest or DI override cannot silently remove a watch feature.

## Material 3 and round screens

Use Wear Material 3 components, not phone Material 3 components scaled down.
Test clipping and focus on both round and square displays.

With `TransformingLazyColumn`, apply the transformation at one ownership level.
Do not cache layout positions with `remember`; positions change as items
transform and scroll.

## Notifications

When the Wear app can receive messages independently, disable phone-to-watch
notification bridging after watch login and restore it at logout. Otherwise the
same event can alert twice.

## Wear Widgets and Remote Compose

Wear OS is evolving Tiles toward Wear Widgets built with Jetpack Glance and
rendered by Remote Compose. Migration may use:

- dual services during rollout (recommended when compatibility and rollback
  matter), or
- a single compatibility service when the supported versions allow it.

Glance and Remote Compose are constrained UI environments. Do not paste normal
Compose modifiers or lifecycle patterns into them without checking support.
See `remote-compose.md`.

## Operational reliability

If test or dogfood builds expire, schedule update reminders before expiry.
Watch update latency can otherwise create sudden active-user loss unrelated to
the new release's code.

## Sources

- Compose for Wear OS: https://developer.android.com/training/wearables/compose
- WhatsApp case study: https://developer.android.com/events/dev-summit/talks/lessons-from-whatsapps-wear-os-journey
- Wear Widgets migration: https://developer.android.com/events/dev-summit/talks/evolving-tiles-to-wear-widgets-using-jetpack-glance-and-remote-compose
