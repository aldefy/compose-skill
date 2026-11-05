# Reliable Text Editing in Compose

## Prefer state-based text fields

For new code, prefer the `TextFieldState` overloads of `TextField`,
`OutlinedTextField`, `BasicTextField`, and `SecureTextField`.

```kotlin
@Composable
fun SearchField() {
    val state = rememberTextFieldState()
    OutlinedTextField(
        state = state,
        label = { Text("Search") },
    )
}
```

`TextFieldState` updates synchronously with the editing session. It avoids the
timing race caused by round-tripping every keystroke through `value` and
`onValueChange`, especially when the software keyboard is composing text.

## Editing programmatically

Mutate text through `edit` so text, selection, and composition stay coherent.

```kotlin
state.edit {
    replace(0, length, "Hello")
    placeCursorAtEnd()
}
```

Do not modify the same `TextFieldState` concurrently from multiple coroutines.
Serialize edits at the state-holder boundary.

## Input and output transformations

- `InputTransformation` can reject or modify user-originated edits before they
  are committed.
- `OutputTransformation` changes presentation without changing stored text and
  without manually maintaining offset mappings.

```kotlin
val digitsOnly = InputTransformation {
    if (!asCharSequence().all(Char::isDigit)) revertAllChanges()
}

TextField(
    state = state,
    inputTransformation = digitsOnly,
)
```

Business validation still belongs outside the text field. An input
transformation is appropriate for editing invariants such as maximum length or
allowed characters, not server validation or cross-field rules.

## Hoisting decision

Keep `TextFieldState` local when only the composable needs editing details.
Hoist it into a screen state holder when multiple composables coordinate edits.
It may live in a `ViewModel` when business logic genuinely needs selection,
composition, or synchronous editing state.

```kotlin
class CommentViewModel : ViewModel() {
    val draft = TextFieldState()

    fun submit() {
        val text = draft.text.toString()
        // Validate and submit text.
    }
}
```

Do not put every field into a ViewModel by default. For process recreation,
persist only the minimal user input needed to restore the draft, not transient
IME composition.

## Observing text

Reading `state.text` in composition is observable. For asynchronous work such
as search, use `snapshotFlow`, debounce if appropriate, and cancel with the
screen lifecycle.

```kotlin
LaunchedEffect(state) {
    snapshotFlow { state.text.toString() }
        .debounce(300)
        .distinctUntilChanged()
        .collect(onQuery)
}
```

## Rich and formatted text

Compose 1.12 adds formatted editing support to `TextFieldBuffer`, including
tracked style ranges and expansion policies. Gate examples on the project's
actual Compose version. The announced markup editor/parser remains future work;
do not invent or recommend a public markup API until it ships.

## Migration checklist

1. Replace `value`/`onValueChange` with a remembered or hoisted `TextFieldState`.
2. Move character filtering into `InputTransformation`.
3. Move visual formatting into `OutputTransformation`.
4. Replace direct string assignment with `state.edit` helpers.
5. Test IME composition, selection, paste, autofill, accessibility, and process
   recreation—not just simple typing.

## Common mistakes

- Recreating `TextFieldState` on every recomposition.
- Launching network work directly from every edit callback.
- Using an output transformation for stored-data validation.
- Copying `state.text` into a second mutable state and creating two sources of truth.
- Stripping newlines or Unicode code points without considering IME composition.

## Sources

- State-based text fields: https://developer.android.com/develop/ui/compose/text/user-input
- Android Dev Summit session: https://developer.android.com/events/dev-summit/talks/building-reliable-text-editing-experiences-in-compose
