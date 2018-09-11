Please ensure pull requests adhere to the following guidelines, it's okay to deviate from them but please have a good reason to do so!

# Coding Styles
* PEP8 is the standard coding style, and should rarely be deviated from. It is recommended that you use a development environment that supports a PEP8 linter to keep your code clean as you work, and will remove the need for refactoring code later.
* As a general rule of thumb, functions should be fewer than ~15-20 lines of code, if a function is longer consider refactoring the code.
* No functions should exceed a [cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity) of 8.
* Do not use single character variable names.
* All non-trival functions and classes should contain docstrings.
* Please create a new branch for your edits (bug fixes, features, etc) and choose an appropriate branch name so we can keep everything nice and organized.

# Secure Coding Practices
### Cross-domain Security
* GET requests may *never* alter application state.
* POST requests *must* contain a CSRF token.
* WebSockets *must* implement the `check_origin` method. This method is implemented by `handlers.WebSocketBaseHandler` for convenience.

### Content Security
* All HTTP responses *must* implement a `Content-Security-Policy` (CSP). 
* The CSP may *never* allow unsafe content sources (e.g. `unsafe-inline`).
* The CSP may *never* contain wildcard sources (e.g. `*.googleapis.com`)
* Data URIs (`data:`) may *never* be allowed as a content source by the CSP.
* Avoid placing user controlled variables within HTML tag attributes, even when escaped.
* Raw output may *never* be used when constructing templates.
* All HTTP responses *must* implement standard HTTP security-headers (e.g. `Content-Type-Options`, etc).
* *Never* use single quotes `'` inside HTML templates, instead use the HTLM entity version `&#x27;` this is to help prevent contextual HTML encoding errors and limit potential dangling markup injection attacks.

### Database Security
* *Never* disclose primary keys (e.g. `id`) for database objects, instead use a UUID.
* *Never* directly query the database, always use SQLAlchemy for database access.
* Use the most narrowly scoped query methods whenever possible (e.g. `by_team_and_uuid` instead of `by_uuid`).
* Unscoped database queries (e.g. `by_id`, `by_uuid`) and similar methods *must* be marked with the `@dangerous` decorator. These methods should only ever be called from handlers that require the `admin` permission.

### Filesystem Security
* *Never* include user controlled data when constructing file paths (no don't try to sanitize it).
* *Always* assume the `files/` directory is the only writable directory by the application at runtime. 
* *Never* alter the application's current working directory.
