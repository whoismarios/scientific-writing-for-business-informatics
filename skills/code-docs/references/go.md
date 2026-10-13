# Go (doc comments)

Source: The Go Authors, *Go Doc Comments* (https://go.dev/doc/comment). Background: *Effective Go*, section "Commentary" (https://go.dev/doc/effective_go#commentary).

The check script does not parse Go. The agent applies these rules when writing. `go doc` and `gopls` show the comments.

## When a doc comment is required

Every exported (capitalized) name, and every package (one package comment, usually in `doc.go` or the main file). Doc comments stand directly before the declaration, with no blank line in between.

## Shape

Go has **no tags** for parameters or return values. They are named in the prose, without backquotes. "Summary, parameters, return value" from the other languages therefore becomes: first sentence states what the function returns or does, further sentences name the parameters and results that need explaining.

```go
// TotalPrice returns the total of order in the smallest unit of currency,
// after all discounts are applied in the order they were added.
// It returns an error if order has no items.
func TotalPrice(order Order, currency string) (int64, error) {
```

- **Complete sentences** that **start with the name** of the declared symbol ("TotalPrice returns ...").
- **Functions:** say what the function returns, or for functions called for side effects, what it does.
- **Booleans:** "reports whether ..." without "or not" ("HasPrefix reports whether the string s begins with prefix.").
- **Several results:** name the results in the signature if that makes the comment easier to follow.
- **Packages:** "Package path implements ..." as the first sentence.
- Lists, links and code blocks follow the doc comment syntax described in the source, not Markdown.
