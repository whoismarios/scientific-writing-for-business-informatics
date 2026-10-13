# Python docstrings (Google style)

Source: Google, *Google Python Style Guide*, section 3.8 "Comments and Docstrings", in particular 3.8.3 "Functions and Methods" (https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings). General docstring conventions: Goodger and van Rossum, *PEP 257 – Docstring Conventions* (https://peps.python.org/pep-0257/). The format is understood by Sphinx through the extension `sphinx.ext.napoleon`.

## When a docstring is required

The guide makes a docstring mandatory for every function that is part of the public API, has a non-trivial size or non-obvious logic (3.8.3), and for every module (3.8.2) and class (3.8.4). A method that overrides a documented base method needs none (3.8.3.1).

The check reports only public functions by default, because a script cannot judge size or obviousness reliably. When documenting a module, also document private helpers whose logic is not obvious, as the guide requires. `private = true` makes the check report them.

## Shape

```python
def fetch_rows(table: Table, keys: Sequence[str], require_all: bool = False) -> dict[str, tuple[str, ...]]:
    """Fetches rows for the given keys from a table.

    Keys that are not found are left out of the result unless require_all is set.

    Args:
        table: Open table handle to read from.
        keys: Row keys to fetch. Duplicates are fetched once.
        require_all: Raise instead of skipping keys that are not found.

    Returns:
        A mapping from each found key to its row as a tuple of strings.

    Raises:
        KeyError: A key is missing and require_all is set.
    """
```

- **Summary line:** one sentence, at most about 80 characters, ending with a period (3.8.1). Descriptive ("Fetches rows ...") or imperative ("Fetch rows ..."), but consistent within a file (3.8.3). In a file without docstrings use the descriptive form. The docstring tells a caller enough to call the function without reading its code, not how it works inside.
- **Body:** optional, after a blank line. Behavior a caller must know: side effects, ordering, caching, units, what happens on empty input.
- **Sections may be left out** when name and signature are informative enough for a one-line docstring (3.8.3). A docstring with a body needs the sections. With `style = "full"` in `code-docs.toml` the project asks for Args and Returns on every function, which is stricter than the guide.
- **Args:** each parameter by name, in signature order. `*args` and `**kwargs` are listed with their stars. Types only when the signature has no type annotation. Hanging indent of two or four spaces, consistent within a file.
- **Returns:** the meaning of the value. For generators **Yields**, describing what `next()` returns. Not needed for `None`, and not needed when the summary starts with "Returns" or "Yields" and already describes the value. A tuple is described as one value ("A tuple (a, b), where ..."), not as several named values.
- **Raises:** exceptions relevant to the interface. Not those raised only when the documented API is violated.
- **Properties:** attribute style ("The number of stored orders."), not "Returns the number ..." (3.8.3).

## Classes and modules

```python
class OrderService:
    """Creates, updates and cancels orders against the database.

    Attributes:
        repository: Data access for orders.
        clock: Source of the current time, replaceable in tests.
    """
```

The class docstring describes what an instance represents. Public attributes go under **Attributes** (3.8.4).

A module starts with a docstring that says what the file contains and how it is used (3.8.2). Test modules need one only if they add information.

## Framework code

- FastAPI, Flask or Django handlers: the summary says what the endpoint does from a client's point of view. Injected dependencies (`db: Session = Depends(...)`) get a short Args entry.
- Pydantic and SQLAlchemy models: a class docstring plus `Attributes` only for fields whose meaning is not obvious from name and type.

## Avoid

- Restating the name: `"""Gets the user."""` on `get_user`. Say what is special: which user, from where, what if none exists.
- Describing the implementation line by line.
- Comments that will be wrong after the next change: line numbers, counts, names of callers.
