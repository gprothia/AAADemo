# Testing rules (workspace)

- Treat each acceptance criterion's Given/When/Then as the test's arrange/act/assert, in that order.
- Assert on the exact status codes, error codes and field names written in the spec.
  If the spec is vague ("returns an error"), flag it in your plan instead of guessing.
- For API tests, validate response bodies against the OpenAPI file named in the spec's
  `api:` front matter when it exists.
- For UI tests, assert on what the user sees (text, enabled/disabled state, URL), not on
  implementation details.
- Name tests after behaviour: `test_rejects_zero_quantity`, not `test_ac2`.
- Never delete or weaken an existing test to make CI green without saying so in the plan.
