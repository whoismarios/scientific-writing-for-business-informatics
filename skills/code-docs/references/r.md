# R (roxygen2)

Sources: *roxygen2*, article "Documenting functions" (https://roxygen2.r-lib.org/articles/rd.html), and the tidyverse team, *Tidyverse style guide*, chapter 7 "Documentation" (https://style.tidyverse.org/documentation.html).

The check script does not parse R. The agent applies these rules when writing. In a package, `devtools::document()` turns the comments into `.Rd` help files.

## When documentation is required

Every exported function. Internal functions are documented the same way and marked with `@noRd`, so no help page is generated (tidyverse 7.9). For a package submitted to CRAN every exported function needs a documented return value (roxygen2, "Outputs").

## Shape

```r
#' Calculate the total price of an order
#'
#' Applies all discounts in the order they were added.
#'
#' @param order A data frame with one row per item and a `price` column.
#' @param currency ISO 4217 code of the result.
#' @returns A single number, the total in the smallest unit of the currency.
#' @export
#' @examples
#' total_price(example_order, "EUR")
total_price <- function(order, currency) {
```

- **Title** (tidyverse 7.2): the first line, sentence case, **no** full stop. Followed by a blank `#'` line and the description.
- **`@param name description`** for every parameter (roxygen2: "All parameters must be documented"). The description names the type and, if not obvious, what the parameter does. A sentence with capital letter and full stop (tidyverse 7.4, 7.5). Tightly coupled parameters can share one entry: `@param x,y Numeric vectors.`
- **`@returns`** briefly describes type and shape of the output, not the details.
- **`@examples`** with code that runs without errors, because `R CMD check` executes it.
- One space after `#'`, continuation lines of a tag indented by two more spaces (tidyverse 7.3).
- Markdown enabled in roxygen2, as the tidyverse guide recommends (7.1).
