# Java (Javadoc)

Source: Google, *Google Java Style Guide*, section 7 "Javadoc" (https://google.github.io/styleguide/javaguide.html#s7-javadoc). Wording of descriptions: Oracle, *How to Write Doc Comments for the Javadoc Tool* (https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html).

The check script does not parse Java. The agent applies these rules when writing.

## When Javadoc is required

Every visible class, member and record component: public top-level classes, and public or protected members of visible classes (7.3). Exceptions:

- simple, obvious members such as `getFoo()` when there is truly nothing to say but "the foo" (7.3.1). Not an excuse to leave out what a reader needs.
- methods that override a supertype method (7.3.2).

Other classes and members get Javadoc where an implementation comment would otherwise describe their purpose (7.3.4).

## Shape

```java
/**
 * Calculates the total price of an order after discounts.
 *
 * <p>Discounts are applied in the order they were added.
 *
 * @param order the order to price, not empty
 * @param currency ISO 4217 code of the result
 * @return the total in the smallest unit of the currency
 * @throws IllegalArgumentException if the order has no items
 */
public long totalPrice(Order order, String currency) {
```

- **Summary fragment** (7.2): a noun or verb phrase, not a full sentence, but capitalized and ending with a period. Not "This method returns ..." and not imperative ("Save the record."). Write "Returns the customer ID." rather than only `@return the customer ID`.
- **Third person** (Oracle): "Gets the label." not "Get the label."
- **Block tags** (7.1.3): in the order `@param`, `@return`, `@throws`, `@deprecated`, never with an empty description. Continuation lines indented four spaces from the `@`.
- **Paragraphs** (7.1.2): blank line with only `*` between paragraphs and before the tags. Each further paragraph starts with `<p>` directly before the first word.
- **Single-line form** `/** Short text. */` only when there are no block tags (7.1.1). Markdown Javadoc with `///` is also allowed (7.1.1). Use the form the project already uses.

## Avoid

- Repeating the name: "Gets the label." on `getLabel()` adds nothing unless it says which label or what happens when none is set (Oracle, "Add description beyond the API name").
- Documenting types again, they are in the signature.
