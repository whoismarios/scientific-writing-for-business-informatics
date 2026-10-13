# C# (XML documentation comments)

Source: Microsoft, *XML documentation comments* (https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/) and *Recommended XML tags for C# documentation comments* (https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/recommended-tags).

The check script does not parse C#. The compiler does part of the work: with `GenerateDocumentationFile` enabled it warns when a `<param>` names a parameter that does not exist or when not all parameters are described. Suggest enabling it in the `.csproj` if the project wants checked documentation.

## When a comment is required

Every public type and member that is part of the API. Comments cannot be applied to namespaces.

## Shape

```csharp
/// <summary>
/// Calculates the total price of an order after discounts.
/// </summary>
/// <param name="order">The order to price. Must contain at least one item.</param>
/// <param name="currency">ISO 4217 code of the result.</param>
/// <returns>The total in the smallest unit of the currency.</returns>
/// <exception cref="ArgumentException">The order has no items.</exception>
public long TotalPrice(Order order, string currency)
```

- **`<summary>`** describes the type or member. It appears in IntelliSense. Supplemental detail goes into `<remarks>`.
- **`<param name="...">`** for each parameter. Once used, the compiler expects all parameters to be described.
- **`<returns>`** for the return value, **`<value>`** for properties, **`<typeparam>`** for generic type parameters.
- **`<exception cref="...">`** for exceptions a caller should handle.
- **`<inheritdoc/>`** on overrides and interface implementations instead of copying text.
- Complete sentences ending with a period. Write `&lt;` and `&gt;` for angle brackets inside text, the comment must be well-formed XML.
