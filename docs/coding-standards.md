# Coding standards — AI anti-patterns

The always-on rubric for this repo. The **impl gate** rejects code that exhibits
any of these, and every implementation is bound by them. Treat it as the
constitution: a spec may not authorize violating it without an explicit, reviewed
justification.

## 1. Defensive fallbacks

Don't wrap code in error handlers "just in case." If something should work, let it
fail visibly when it doesn't.

- Don't catch import/require errors and fall back to a stub or nil. If a
  dependency is required, let the failure surface.
- Don't use fallback accessors (`getattr(obj, "x", default)`, `?.`, `?? fallback`,
  `|| default`) on values that must exist. Access them directly — crash if the
  contract is violated.
- Don't guard against null/None/undefined when the value is guaranteed by the API
  contract. Unnecessary null checks hide real bugs by silently skipping code that
  should have run.

## 2. Error hiding

Never swallow errors silently. Catch-all handlers that discard or merely log
errors hide real bugs.

- No bare catch-all blocks that do nothing (`catch {}`, `except: pass`).
- No broad catches that log-and-continue — the caller thinks it succeeded.
- Catch only specific, expected error types. Let unexpected errors propagate.
- Handle errors only at system boundaries (user input, network, file I/O), not
  around internal logic that should always succeed.

## 3. Unnecessary abstractions

Don't create helpers, base classes, wrappers, or factories for one-time
operations. Three similar lines beat a premature abstraction. Don't design for
hypothetical future requirements.

## 4. Compatibility shims

Don't add backward-compatibility code unless explicitly requested. No old-name
aliases, no deprecated re-exports, no version-checking conditionals when the
project has a fixed minimum version.

## 5. Cheating / fake implementation

No fallback-with-hardcoding (`try: real() except: return <hardcoded>`), no stubbed
returns that make a criterion pass without real behavior, no tests asserting
trivialities, no behavior special-cased to the test's inputs. The criteria measure
real behavior or they are worthless.

This extends to **evidence**. A spike `verify` that hardcodes or echoes its conclusion,
never invokes the real subject under question, reads a fixture it authored, or measures a
convenient *neighbour* of the claim (a smaller input, the wrong version, a mocked
dependency, a proxy metric, the happy path of a "for all" claim) is a **false spike** —
fabricated evidence — even if it runs and reproduces. Evidence must exercise the claim's
actual subject and quantifier.
