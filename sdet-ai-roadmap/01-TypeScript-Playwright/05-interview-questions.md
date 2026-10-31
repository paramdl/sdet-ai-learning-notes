# TypeScript + Playwright — Interview Questions & Answers

> Answer format that works: **definition → your real example → trade-off you know about.** The third part is what makes you sound like someone who has actually shipped this.

---

# Part 1 — TypeScript

**Q1. Why TypeScript over JavaScript for test automation?**
Errors surface at compile time instead of halfway through a 40-minute CI run. Autocomplete on page objects and fixtures makes the framework self-documenting. Refactoring is safe — rename a page object method and the compiler finds every caller. The cost is a build step and slightly slower iteration, which UI mode and `tsx` mostly erase.

**Q2. `any` vs `unknown` vs `never`?**
`any` disables type checking and spreads silently through a codebase. `unknown` accepts anything but forces you to narrow before use — this is what I use for API responses. `never` is a value that can't occur; I use it for exhaustiveness checks in switch statements so a new union member becomes a compile error instead of a runtime surprise.

**Q3. `interface` vs `type`?**
Interfaces describe object shapes, extend cleanly, and support declaration merging — which matters when augmenting third-party types like Playwright fixtures. Type aliases handle everything else: unions, intersections, function signatures, mapped and conditional types. I default to `interface` for objects and `type` for the rest.

**Q4. What are generics and where have you used them?**
Generics let a function or class work over many types while preserving type information. In my framework I have `apiGet<T>(url): Promise<ApiResponse<T>>` so the caller gets a fully typed response, and a `Repository<T extends { id: number }>` for test data pools.

**Q5. Explain `keyof` and `typeof`.**
`keyof T` produces a union of T's property names. `typeof x` in a type position gives the type of a value. Together: `function get<T, K extends keyof T>(o: T, k: K): T[K]` — a getter that returns the exact property type, and rejects invalid keys at compile time.

**Q6. Name five utility types and a real use for each.**
`Partial<T>` for test data factories with overrides. `Pick`/`Omit` for building request payloads from a full model. `Record<K,V>` for env-to-URL maps where forgetting an env is a compile error. `ReturnType<typeof fn>` for typing a helper's output without duplicating it.

**Q7. What is a discriminated union?**
A union where each member has a literal field identifying it. TypeScript narrows on that field, so inside `if (r.ok)` it knows `data` exists. I model API results this way rather than throwing, so callers are forced to handle the error branch.

**Q8. What's a type guard?**
A function returning `obj is Type` that tells the compiler what something is after a runtime check. I use `isUser(data)` after `await res.json()` so an unexpected API shape fails loudly at the boundary instead of as `undefined is not a function` three layers deep.

**Q9. `??` vs `||`?**
`||` falls through on any falsy value, including `""` and `0`. `??` only falls through on `null` or `undefined`. For config, `port ?? 3000` is correct — `port || 3000` would wrongly override a valid port of 0.

**Q10. What does `as const` do?**
Freezes a value to its literal type and makes it deeply readonly. `const ROLES = ['admin','user'] as const` gives `readonly ["admin","user"]`, and `typeof ROLES[number]` becomes the union `"admin" | "user"` — one source of truth for both the array and the type.

**Q11. `Promise.all` vs `allSettled` vs `race`?**
`all` rejects on the first failure — use when all must succeed. `allSettled` always resolves with per-promise outcomes — use when you want every result even if some fail, like health-checking 20 endpoints. `race` settles on the first to finish — use for timeouts.

**Q12. How do you type errors in a catch block?**
`catch (e: unknown)`, then narrow with `instanceof`. TypeScript types catch as `unknown` under `useUnknownInCatchVariables` because anything can be thrown, not just Errors. I define custom error classes like `ApiError` with status and url so tests can assert on them.

**Q13. What is declaration merging and where does it matter for Playwright?**
Two interface declarations with the same name merge. It matters when extending Playwright's types — for example augmenting `TestInfo` or adding custom matcher types via `declare global`.

**Q14. Explain mapped and conditional types.**
A mapped type transforms every property: `{ [K in keyof T]: T[K] | null }`. A conditional type branches on a type: `T extends Promise<infer U> ? U : T`. `infer` extracts a type from a position. Together they build things like `DeepReadonly<T>`.

**Q15. What's the difference between compile-time and runtime in TypeScript?**
All types are erased at compile time — they don't exist at runtime. This is why you can't do `if (x instanceof MyInterface)`. Runtime validation needs actual code: type guards, or a schema library like Zod. This trips people up when validating API responses.

---

# Part 2 — Playwright fundamentals

**Q16. Why Playwright over Selenium or Cypress?**
Playwright has auto-waiting built into every action, real cross-browser support including WebKit, true parallel isolation via browser contexts, native API testing, and trace viewer for debugging CI failures. Against Cypress specifically: multi-tab and multi-origin work properly, and tests run in Node rather than inside the browser. Selenium's advantage is language breadth and a much older ecosystem; Playwright's is developer experience and speed.

**Q17. What is auto-waiting?**
Before acting, Playwright checks the element is attached, visible, stable, enabled, and receives events. It retries until the timeout. This removes most explicit waits — which is why `waitForTimeout` in a Playwright codebase is almost always a sign someone didn't trust the framework.

**Q18. Locator vs ElementHandle?**
A locator is lazy — it describes how to find an element and re-resolves on every use, so it survives re-renders. An ElementHandle points at a specific DOM node and goes stale. Always use locators. ElementHandle exists mainly for legacy interop.

**Q19. What's your locator priority?**
Role first, then label, placeholder, text, alt, title, then test ID, and CSS or XPath only as a last resort. Role-based locators test what the user and assistive tech actually perceive, and they don't break when someone changes a class name.

**Q20. Difference between `fill` and `pressSequentially`?**
`fill` sets the value in one operation — fast, and correct for most cases. `pressSequentially` sends individual keystrokes, which you need for autocomplete, input masks, or anything with per-keystroke JS listeners.

**Q21. How does `expect(locator)` differ from `expect(value)`?**
Locator assertions auto-retry until they pass or time out. Value assertions evaluate once. So `await expect(locator).toHaveText('x')` waits for the text to appear, while `expect(await locator.textContent()).toBe('x')` snapshots once and is flaky.

**Q22. What are soft assertions?**
`expect.soft()` records a failure but lets the test continue, so one run reports multiple problems. Useful for validating many fields on a page. The test still fails at the end. Don't use them for preconditions — if login failed, continuing is pointless.

**Q23. `expect.poll` vs `expect.toPass`?**
`poll` retries a function until its returned value satisfies a matcher — good for polling an API status field. `toPass` retries a whole block of assertions — good when several things must become true together, like an async job completing.

**Q24. How do browser, context, and page relate?**
Browser is the process. A context is an isolated session inside it — its own cookies, storage, cache. A page is a tab within a context. Contexts are cheap, so each test gets a fresh one. That's how Playwright gets isolation without relaunching browsers.

**Q25. How do you handle authentication efficiently?**
Log in once in a setup project, save `storageState` to JSON, and point test projects at that file via `dependencies`. Tests start already authenticated — no repeated login. For multiple roles I save one state file per role and run them as separate projects. Faster still is authenticating via API and injecting the token.

---

# Part 3 — Playwright advanced

**Q26. What are fixtures and why do they beat `beforeEach`?**
Fixtures are dependency-injected setup. They're lazy — only created if a test asks for them — composable, and they carry their own teardown after `use()`. `beforeEach` runs for every test in scope whether needed or not, and sharing state means module-level variables. Fixtures also come in worker scope for expensive one-per-process setup like an auth token.

**Q27. Test scope vs worker scope?**
Test-scoped fixtures are recreated per test — page objects, fresh data. Worker-scoped are created once per worker process — an API token, a seeded database, a Docker container. Worker scope trades isolation for speed, so only use it for things genuinely safe to share.

**Q28. How do you achieve parallelism, and what breaks?**
Playwright runs files in parallel across workers by default, and `fullyParallel: true` parallelises tests within a file too. What breaks: shared mutable state, tests that depend on execution order, fixed test data two tests both mutate, and rate-limited external services. The fix is unique data per test — timestamped emails, per-worker accounts.

**Q29. How do you deal with a flaky test?**
First, reproduce it: `--repeat-each=20`. Then find the category. Timing flake means a missing condition wait — fix with a proper assertion, never a sleep. Data flake means shared state — fix with unique per-test data. Environment flake means the app or a dependency is genuinely unstable — that's a bug report, not a test fix. Retries mask flake; they don't fix it, and a permanently-retried test is a lie about your suite's health.

**Q30. What's in a trace and when do you use it?**
A trace records every action with DOM snapshots, network, console, and source. `trace: 'retain-on-failure'` in config, then `npx playwright show-trace`. It's the single best tool for a CI failure you can't reproduce locally — you get time-travel through the exact failing run.

**Q31. How do you mock network responses?**
`page.route()` with a glob or predicate, then `fulfill` with mock data, `abort` to simulate failure, or `continue` to modify the request. I use it to test error states that are hard to trigger — a 500, a timeout, an empty list — and to block images and analytics for speed.

**Q32. How do you test file downloads?**
Set up `page.waitForEvent('download')` in a `Promise.all` alongside the click that triggers it — the listener must exist before the action. Then `download.saveAs(path)` and assert the file exists with the right size or content.

**Q33. How do you test something across two logged-in users?**
Two browser contexts in one test, each with its own `storageState`. User context sends a message, admin context asserts it appeared. Contexts are fully isolated, so no cookie bleed.

**Q34. How do you handle iframes and shadow DOM?**
Iframes need `page.frameLocator('#id')` and chain from there; nested frames chain again. Shadow DOM needs nothing special — Playwright's locators pierce open shadow roots automatically. Closed shadow roots aren't accessible, which is a genuine limitation.

**Q35. How do you structure a framework for maintainability?**
Layers: tests (intent only), page objects (interaction), components (reusable UI parts), fixtures (setup and injection), API clients (backend calls), data factories, and utilities. Tests never touch selectors; page objects never assert business rules. I prefer composition over deep page inheritance.

**Q36. How do you do visual regression, and what goes wrong?**
`toHaveScreenshot()` with baselines committed to the repo. What goes wrong: font rendering differs between OSes, so baselines must be generated in the same environment as CI — usually Docker. Dynamic content needs masking. Animations need disabling. Without that, visual tests become the flakiest part of a suite.

**Q37. How do you run this in CI?**
Docker image with browsers pre-installed, sharded across parallel jobs, blob reports merged at the end, HTML report and traces published as artifacts. Two retries in CI, zero locally. `forbidOnly: true` so a stray `test.only` fails the build instead of silently skipping the suite.

**Q38. How do you decide what to automate?**
Risk and frequency. Automate revenue paths, auth, and anything that has broken before. Don't automate one-off exploratory checks, rapidly-changing UI, or things cheaper to verify by eye. A 200-test suite covering the right 200 things beats 2000 tests covering everything shallowly — and the 2000 will be flaky.

**Q39. UI test vs API test — how do you split?**
Test business logic, validation, and error handling at the API level — fast and stable. Use UI tests for what only the UI can verify: rendering, user flows, integration between components. Most teams have this inverted, with heavy UI suites testing logic that an API test would cover in 50 ms.

**Q40. How would you convince a team to adopt Playwright?**
Not with a slide deck. Port the ten flakiest existing tests, run both suites side by side for two weeks, and show the numbers: pass rate, runtime, debugging time. Migration is the real cost, so I'd run both in parallel and move suites incrementally rather than proposing a big-bang rewrite.

---

# Part 4 — Scenario questions

**Q41. A test passes locally but fails in CI. Walk me through it.**
Open the trace from the CI run first — that usually ends it. Common causes in order: viewport differences changing what's visible, timing under lower CI resources, missing environment variables, test data that exists locally but not in CI, timezone or locale differences, and animations that complete faster on a fast machine. Running the same Docker image locally eliminates most of the guesswork.

**Q42. Your suite takes 45 minutes. Get it to 10.**
Measure first — find the slowest tests. Then: shard across parallel CI jobs, move logic-level assertions from UI to API, authenticate via API instead of the login form, block images and third-party scripts, reuse contexts where isolation allows, and delete tests that duplicate coverage. Parallelism gives the biggest win, but only after shared-state problems are fixed.

**Q43. How do you test a feature that isn't built yet?**
Write the test cases from the spec and mark them `test.fixme`. It documents intent, keeps the gap visible in the report, and means the day the feature lands you remove one annotation rather than writing from scratch. I also review the spec for testability gaps at that point — that's usually when I find missing error-state definitions.

**Q44. The dev says "it works on my machine." What do you do?**
Give them the trace, the exact build, the environment, and the steps. Not a description — the artefact. Most of the time the trace shows the actual difference: a different API response, a feature flag, stale cached assets. If it genuinely doesn't reproduce, I bisect the environment differences rather than arguing.

**Q45. You have two days before release and 200 tests that take 4 hours. What do you run?**
Risk-based. Smoke on the revenue path first, then anything touching the code that changed, then regression around historically fragile areas. I'd have the suite tagged for exactly this — `@smoke`, `@critical` — so it's a grep, not a judgement call under pressure. And I'd report what I chose not to run, so the release decision is informed rather than assumed.

---

## How to prepare

- [ ] Write out answers to Q1–Q15 in your own words. Don't memorise mine.
- [ ] For every framework question, have a specific example ready from **your own repos** — the QA framework template, a build-verification suite, the API suites.
- [ ] Practise Q29, Q41, and Q42 out loud. Flakiness and speed are the two things every interviewer asks about, and the answers reveal whether you've run a real suite.
- [ ] Prepare one story about a bug you found that mattered. Your CORS-any-origin and user-enumeration findings are strong material — impact, how you found it, what happened next.

---

**Next:** `../02-DevOps/01-git-commands.md`
