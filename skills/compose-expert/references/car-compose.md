# In-Car Apps (Android Auto and Android Automotive OS)

> Two different car surfaces. **While driving**, UI is template-based: apps built
> with the Android for Cars App Library (`androidx.car.app`) describe screens with
> library templates and the host renders them — do not plan on arbitrary Compose
> screens. **While parked**, video, game, and browser apps can run as ordinary
> adaptive Compose apps (see "Parked apps" below).

Google treats driver distraction as a hard constraint. An app must belong to a
supported category and meet car design and quality requirements before it can be
listed on Google Play for Android Auto and Android Automotive OS.

## What Compose is (and is not) for here

| Surface | UI technology |
|---|---|
| Car display while driving (navigation, POI, IoT, weather, media, messaging, calling) | Car App Library templates (`Screen`, `Template`) — not Compose |
| Your phone app, tablet app, settings and onboarding screens | Compose, as usual |
| Shared business logic, repositories, state | Plain Kotlin / KMP, reusable by the car `Screen` and Compose screens |

Design the car experience as a small, glanceable, templated surface backed by
the same domain layer as the phone UI. Do not try to reuse composables on the
car screen.

## Categories

Declare one or more categories in the `CarAppService` intent filter:

- `androidx.car.app.category.NAVIGATION`
- `androidx.car.app.category.POI` (parking, charging, fuel)
- `androidx.car.app.category.IOT`
- `androidx.car.app.category.WEATHER`
- `androidx.car.app.category.MEDIA` (templated media apps)
- `androidx.car.app.category.MESSAGING`
- `androidx.car.app.category.CALLING`

Qualifying criteria per category are defined in Android app quality for cars.

## Project structure

- Implement a `CarAppService` and declare it in the manifest with its category.
- Android Auto apps declare template capability in
  `res/xml/automotive_app_desc.xml`:

  ```xml
  <automotiveApp>
      <uses name="template" />
  </automotiveApp>
  ```

- For Android Automotive OS, add an automotive module that depends on
  `androidx.car.app:app-automotive`, which provides the `CarAppActivity`
  required to run on AAOS.
- When supporting both, keep `CarAppService` and screens in a shared module and
  depend on it from the mobile and automotive modules.

## State and Compose interop

- Own state outside the UI layer (ViewModel/state holder/repository) and expose
  `StateFlow`. Phone Compose screens collect it; car `Screen`s observe it and
  call `invalidate()` when content changes.
- Car screens are bound to the car host lifecycle, not an `Activity`. Do not
  capture phone `Context`, `Activity`, or composition-scoped objects in a car
  `Screen`.
- Keep template content small and rate-limited; the library enforces limits on
  items and navigation depth.

## Parked apps (video, games, browsers)

Parked apps run on Android Auto and Android Automotive OS only while the vehicle
is parked, so a regular adaptive Compose app can be the UI. Only three categories
qualify; other categories cannot be published as parked apps. Availability
varies: video is generally available on Android Automotive OS and unsupported on
Android Auto; games are generally available on both; browsers are beta on
Android Automotive OS only. Audio while driving is a separate beta feature.

Compose-relevant requirements (from the official `android-for-cars-parked-apps`
skill):

- **Manifest:** video sets `android:appCategory="video"`; games set `"game"`;
  browsers add `android.intent.category.APP_BROWSER` to an exported `MAIN`
  activity. Android Auto needs `CAR_LAUNCHER` on the `MAIN` intent filter;
  Android Automotive OS needs `android.hardware.type.automotive` declared. Never
  add `distractionOptimized` to a parked app activity.
- **Display continuity:** handle `screenSize`, `smallestScreenSize`,
  `orientation`, `screenLayout`, and `density` in `android:configChanges` so
  moving to a distant display does not recreate the activity or stutter playback.
  Do not request an orientation the display lacks: check
  `FEATURE_SCREEN_LANDSCAPE` / `FEATURE_SCREEN_PORTRAIT` first.
- **Back navigation:** Android Automotive OS vehicles are not required to have a
  back button or gesture. Provide explicit in-app back and close controls on
  non-root screens, unless compatibility mode
  (`android.software.car.display_compatibility`) is declared and active — then
  hide the duplicate affordance.
- **Insets:** OEMs may lock system bars visible. Track controllable bars with
  `OnControllableInsetsChangedListener`, and protect UI with
  `WindowInsets.safeDrawing`. For irregular display cutouts set
  `windowLayoutInDisplayCutoutMode` to `3` (always) or `2` (never) in
  `res/values-car-v30/integers.xml`; do not use the default or short-edges modes.
- **Driver distraction lifecycle:** when the vehicle moves, the OS covers the
  activity and calls `onPause` (and `onStop` on compatibility-mode vehicles).
  Pause playback on `ON_PAUSE`/`ON_STOP` with `LifecycleEventEffect`, expose a
  Media3 `MediaSession`, and stop external controls from resuming playback while
  `CarUxRestrictionsManager` reports distraction optimization is required.
- **Browsers:** block saved passwords and payment methods unless protected by a
  profile lock, and prompt before syncing sensitive data to the car.

Test against the car app quality tiers (Car ready, Car optimized, Car
differentiated), and cover both Android Auto and Android Automotive OS — they are
separate platforms.

## Driving rules to design for

- Minimize required attention: short text, large targets, few steps.
- Follow the Design for Driving guidelines: avoid video, long-form reading, and
  free-form text entry while driving; prefer voice and short choices.
- Make failures actionable and brief; do not strand the driver on an error.
- Test with the Desktop Head Unit (Android Auto) and the Android Automotive OS
  emulator, then on real hardware when possible.

## Testing

- Verify each template path against the category's quality checklist.
- Test process death and reconnect while connected to a head unit.
- Test with and without network, location, and notification permissions.
- Verify the phone app still works when the car screen is disconnected.

## Sources

- Official parked-apps agent skill: https://github.com/android/skills/tree/main/cars/android-for-cars-parked-apps
- Android for Cars App Library overview: https://developer.android.com/training/cars/apps
- Set up your project (categories): https://developer.android.com/training/cars/apps/library/set-up-project
- Android Automotive OS apps: https://developer.android.com/training/cars/apps/automotive-os
- App quality for cars: https://developer.android.com/docs/quality-guidelines/car-app-quality
- Car App Library release notes: https://developer.android.com/jetpack/androidx/releases/car-app
