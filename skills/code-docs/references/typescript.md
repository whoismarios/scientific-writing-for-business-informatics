# TypeScript and JavaScript (JSDoc)

Source: Google, *Google TypeScript Style Guide*, section "Comments and documentation" (https://google.github.io/styleguide/tsguide.html#comments-documentation), in particular "Document all top-level exports of modules", "Method and function comments" and "JSDoc type annotations". For plain JavaScript: Google, *Google JavaScript Style Guide*, section 7 "JSDoc" (https://google.github.io/styleguide/jsguide.html#jsdoc). Tag syntax: *JSDoc* (https://jsdoc.app/), for TypeScript also *TSDoc* (https://tsdoc.org/).

## When a comment is required

All top-level exports of a module. Also properties and methods, exported or not, whose purpose is not obvious from their name. Symbols exported only for tooling need none. Use `/** ... */` for documentation and `//` for implementation notes ("JSDoc vs comments").

## Shape

```ts
/**
 * Formats a price in cents as a localized currency string.
 *
 * Negative amounts are shown with a minus sign, not in parentheses.
 *
 * @param cents Amount in euro cents.
 * @param locale BCP 47 locale, defaults to German.
 * @returns The formatted price, such as "12,50 €".
 * @throws RangeError If cents is not a finite number.
 */
export function formatPrice(cents: number, locale = "de-DE"): string {
```

- **Summary:** a verb phrase in the third person, as if "This method ..." stood before it ("Method and function comments").
- **Parameter and return descriptions may be left out** when they are obvious from the name and type signature (same section). Once some parameters are documented with `@param`, the check expects all of them, so the comment stays complete. This is a convention of code-docs, modeled on the Args rule of the Python guide. With `style = "full"` every exported function needs `@param` and `@returns`, which is stricter than the guide.
- **`@param name description`:** in TypeScript without `{type}`, types in JSDoc are redundant there ("JSDoc type annotations"). In plain JavaScript add the type: `@param {number} cents`.
- **Destructured parameters:** document the object under one name (`@param props`) or document the fields on the props type instead, one comment per field.
- **`@returns`:** what the value means. Leave out for `void` and `Promise<void>`. If the summary starts with "Returns" and says it all, it may be left out.
- **`@throws`:** only errors that are part of the contract.

## React components and Next.js files

```tsx
/** Card with the status and the next step of one study participant. */
export function ParticipantCard({ participant, onOpen }: ParticipantCardProps) {
```

```ts
interface ParticipantCardProps {
  /** Participant shown on the card. */
  participant: Participant;
  /** Called when the card is clicked. */
  onOpen?: () => void;
}
```

Document props on the props type, so editors show them at every use. Next.js `page`, `layout` and `route` files get a one-line summary of what the route shows or does. Route handlers (`GET`, `POST`) say what they return and which status codes they use.

## Avoid

- Types inside JSDoc in TypeScript files, they drift from the signature.
- `@param` tags that only repeat the name ("@param id The id.").
- Commented-out code.
