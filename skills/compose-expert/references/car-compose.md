# In-Car Apps (Android Auto and Android Automotive OS)

> Driving UI is template-based. Apps built with the Android for Cars App Library
> (`androidx.car.app`) describe screens with library templates; the host renders
> them. Do not plan on putting arbitrary Compose screens on the car display
> while driving.

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

- Android for Cars App Library overview: https://developer.android.com/training/cars/apps
- Set up your project (categories): https://developer.android.com/training/cars/apps/library/set-up-project
- Android Automotive OS apps: https://developer.android.com/training/cars/apps/automotive-os
- App quality for cars: https://developer.android.com/docs/quality-guidelines/car-app-quality
- Car App Library release notes: https://developer.android.com/jetpack/androidx/releases/car-app
