# PlantUML in AsciiDoc

Conventions for PlantUML diagrams, both embedded in `.adoc` files and in
standalone `.puml` files. Class diagrams are the default and preferred diagram
type.

## Embedding in AsciiDoc

Use a titled `[plantuml]` block with `....` delimiters:

```asciidoc
.My Diagram Title
[plantuml]
....
hide circles
hide empty members

class foo as "The Foo"<<myType>>
....
```

## Standalone .puml files

```plantuml
@startuml
hide circles
hide empty members
' ... main content
@enduml
```

## Baseline rules

- **Always** start with `hide circles` and `hide empty members`.
- **Ordering:** first styling, then all class declarations, then all relations.
- **Class syntax:** `class` lowerCamelCase `as "Title Cased Label"`, with an
  optional `<<lowerCamelCase>>` stereotype. The stereotype MUST come after the
  quoted display name:

```plantuml
class userAccount as "User Account"<<portal>>
```

- **Diagram types:** use class diagrams for almost everything. State diagrams
  and sequence diagrams are fine. Component diagrams almost never.

## Making it readable: typed + styled classes

### 1. Assign logical types as stereotypes

Give each class its logical type (context-dependent) as a stereotype; omit the
stereotype when there is no logical type to state:

```plantuml
class user as "User"<<portal>>
class admin as "Admin"<<portal>>
class shop as "Shop"<<commerce>>
```

A type with just one instance should NOT get the color-plus-legend treatment —
assign the type and simply do not hide its stereotype, so it renders on the
class itself.

### 2. Style the types

Hide every stereotype that is used for styling, then color each type with
`BackgroundColor`, `BorderColor`, and `FontColor` (hex `#ff6900` or keyword
`lightgray`):

```plantuml
hide <<portal>> stereotype
hide <<commerce>> stereotype

skinparam class {
  BackgroundColor<<portal>> lightgray
  BackgroundColor<<commerce>> lightblue
  BorderColor<<commerce>> green
  FontColor<<commerce>> darkgray
}
```

IMPORTANT — styling syntax: use the classic `skinparam class` stereotype form
shown above, NOT a `<style>` block. In PlantUML 1.2026.x the `<style>`-block
stereotype selectors (`.portal { BackgroundColor ... }`, including nested
`classDiagram { class { ... } }` forms) do not apply to classes declared with
an `as "display name"` alias — the boxes render white — and
`skinparam useBetaStyle true` is a no-op. Since these conventions always alias
classes (`as "Label"`), the skinparam form is the only one that colors them
correctly. When encountering an existing diagram styled with a `<style>` block,
convert it to the skinparam form.

### 3. Add a Legend package

Create a package called `Legend` in which each styled type appears exactly
once:

```plantuml
package Legend {
  class legend_portal as "Portal"<<portal>>
  class legend_commerce as "Commerce"<<commerce>>
}
```

## Emoji styling

When classes carry a small (max 7) set of non-exclusive binary flags or
enum-like types, represent them as emoji in the class label:

- If each class has zero or one emoji: put it at the **start** of the label,
  followed by a space (`class cart as "🛒 Cart"`).
- If multiple emoji per class: put them at the **end** (label, space, emojis).
- Define PlantUML variables for the emoji (see
  [PlantUML preprocessing](https://plantuml.com/preprocessing)):

```plantuml
!$paid = "💰"
!$beta = "🧪"

class checkout as "Checkout $paid$beta"
```

- If emoji are used, the Legend must explain each one.

## Hyperlinks in diagrams

To make diagram elements clickable, use PlantUML link syntax — see
[plantuml.com/link](https://plantuml.com/link):

```plantuml
class shop as "Shop" [[https://example.com/shop{Shop docs}]]
```

## Checklist for reviewing a diagram

1. `hide circles` and `hide empty members` present (or `@startuml` wrapper plus
   both, for `.puml` files).
2. Order: styling → classes → relations.
3. Class names lowerCamelCase, display labels Title Cased via `as "..."`,
   stereotype after the quoted name.
4. Styling uses `skinparam class { ...<<type>>... }`, not a `<style>` block.
5. Every styled stereotype is hidden; single-instance types are unstyled and
   unhidden instead.
6. `Legend` package present when types are color-styled; explains emoji if any.
7. Diagram type is class (or state/sequence when genuinely appropriate).
