# Media3 UI in Compose

## Player ownership

Own the `Player` in a lifecycle-aware state holder. A composable renders player
state and sends commands; it should not create a new ExoPlayer during ordinary
recomposition.

Release the player at the lifecycle boundary that owns it. Do not rely on a
leaf composable's `DisposableEffect` when playback must survive navigation.

## Media3 UI Compose

Media3 provides ready-made player composables and smaller building blocks. Use
the full component for standard playback, or replace specific control slots
while retaining the library's player-state synchronization.

Prefer slots and documented state adapters over polling the player from a
`LaunchedEffect`. Keep accessibility labels, focus order, keyboard shortcuts,
and large-screen controls when customizing.

## Local and Cast playback

The modern `CastPlayer` implements the standard Player interface and delegates
between local and remote playback. UI should observe the shared Player contract
rather than branching throughout the composable tree on local versus Cast.

Preserve media item, position, play state, and error transitions when changing
the active player.

## Form factors and power

- Adapt controls for touch, keyboard, D-pad, rotary, and car templates where
  applicable.
- Keep video UI resizable and avoid fixed aspect-ratio assumptions.
- Use supported audio offload modes for screen-off playback.
- Test background/foreground, audio focus, route changes, and process recreation.

## Sources

- Media3 UI Compose: https://developer.android.com/media/media3/ui/compose
- Dev Summit Media3 session: https://developer.android.com/events/dev-summit/talks/optimize-media-playback-and-maximize-reach-with-jetpack-media3-apis
