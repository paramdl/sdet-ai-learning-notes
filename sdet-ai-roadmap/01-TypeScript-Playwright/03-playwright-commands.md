# Playwright — Complete Command & API Reference

---

## 1. Install and scaffold

```bash
# new project, interactive scaffold
npm init playwright@latest

# with answers pre-supplied
npm init playwright@latest -- --quiet --browser=chromium --browser=firefox --lang=ts

# add to an existing project
npm install -D @playwright/test
npx playwright install                 # download browser binaries
npx playwright install chromium        # just one
npx playwright install --with-deps     # + OS deps (needed in Docker/CI)
npx playwright install-deps            # OS deps only

# check version
npx playwright --version
```

---

## 2. Running tests — every flag you need

```bash
npx playwright test                              # all tests
npx playwright test tests/login.spec.ts          # one file
npx playwright test tests/auth/                  # one folder
npx playwright test -g "login"                   # by title (grep)
npx playwright test --grep-invert "slow"         # exclude by title
npx playwright test --project=chromium           # one project
npx playwright test --project=chromium --project=firefox

npx playwright test --headed                     # see the browser
npx playwright test --debug                      # Playwright Inspector
npx playwright test --ui                         # UI mode — best for development
npx playwright test --trace on                   # always record trace
npx playwright test --trace retain-on-failure

npx playwright test --workers=4                  # parallel workers
npx playwright test --workers=1                  # serial
npx playwright test --fully-parallel             # parallelise within files too

npx playwright test --retries=2
npx playwright test --repeat-each=5              # flake hunting
npx playwright test --max-failures=1             # fail fast

npx playwright test --reporter=list
npx playwright test --reporter=html,json
npx playwright test --reporter=line --reporter=github

npx playwright test --shard=1/4                  # CI sharding
npx playwright test --last-failed                # rerun only failures
npx playwright test --only-changed               # only tests touching changed files

npx playwright test --timeout=60000
npx playwright test --global-timeout=600000
npx playwright test --update-snapshots           # accept new visual baselines
npx playwright test --list                       # list without running
```

### Reports and traces

```bash
npx playwright show-report                       # open last HTML report
npx playwright show-report path/to/report
npx playwright show-trace trace.zip
npx playwright show-trace test-results/.../trace.zip
```

---

## 3. Codegen, inspection, utilities

```bash
npx playwright codegen                           # record a script
npx playwright codegen https://example.com
npx playwright codegen --target=javascript
npx playwright codegen --save-storage=auth.json  # save login state while recording
npx playwright codegen --load-storage=auth.json  # start already logged in
npx playwright codegen --device="iPhone 13"
npx playwright codegen --viewport-size=1280,720
npx playwright codegen --color-scheme=dark

npx playwright open https://example.com          # browse with Playwright
npx playwright screenshot https://example.com shot.png
npx playwright screenshot --full-page https://example.com shot.png
npx playwright pdf https://example.com page.pdf

npx playwright merge-reports ./blob-reports      # combine shards
npx playwright clear-cache
```

---

## 4. `playwright.config.ts` — annotated

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  snapshotDir: './snapshots',

  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,       // undefined = half your cores
  retries: process.env.CI ? 2 : 0,
  forbidOnly: !!process.env.CI,                  // fail CI if test.only is left in

  timeout: 30_000,                               // per test
  globalTimeout: 20 * 60_000,                    // whole run
  expect: { timeout: 10_000 },                   // per assertion

  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'results.json' }],
    ['junit', { outputFile: 'results.xml' }],    // for Jenkins
  ],

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',                  // 'on' | 'off' | 'on-first-retry'
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    ignoreHTTPSErrors: true,
    locale: 'en-IN',
    timezoneId: 'Asia/Kolkata',
    viewport: { width: 1280, height: 720 },
    extraHTTPHeaders: { 'x-test-run': 'true' },
  },

  projects: [
    { name: 'setup', testMatch: /global\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'auth/user.json' },
      dependencies: ['setup'],
    },
    { name: 'firefox',  use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit',   use: { ...devices['Desktop Safari'] } },
    { name: 'mobile',   use: { ...devices['iPhone 13'] } },
    { name: 'api',      use: { baseURL: process.env.API_URL } },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

---

## 5. Locators — the priority order

Use them in this order. Higher ones survive refactors and test what the user actually sees.

```typescript
// 1. Role — best. mirrors the accessibility tree
page.getByRole('button', { name: 'Submit' });
page.getByRole('link', { name: 'Home', exact: true });
page.getByRole('textbox', { name: 'Email' });
page.getByRole('heading', { level: 1 });
page.getByRole('checkbox', { checked: true });
page.getByRole('row', { name: 'Alex' });

// 2. Label — for form fields
page.getByLabel('Password');
page.getByLabel('Remember me', { exact: true });

// 3. Placeholder
page.getByPlaceholder('Search products');

// 4. Text
page.getByText('Welcome back');
page.getByText('Welcome', { exact: false });
page.getByText(/welcome/i);

// 5. Alt text — images
page.getByAltText('Company logo');

// 6. Title attribute
page.getByTitle('Close dialog');

// 7. Test ID — when semantics genuinely aren't available
page.getByTestId('submit-button');

// 8. CSS / XPath — last resort, brittle
page.locator('.btn-primary');
page.locator('#username');
page.locator('//button[@type="submit"]');
```

> Configure the test-id attribute name if your app uses something else:
> `use: { testIdAttribute: 'data-qa' }`

### Filtering and chaining

```typescript
// filter by text
page.getByRole('listitem').filter({ hasText: 'Product 2' });
page.getByRole('listitem').filter({ hasNotText: 'Out of stock' });

// filter by nested element
page.getByRole('listitem').filter({ has: page.getByRole('button', { name: 'Buy' }) });
page.getByRole('row').filter({ hasNot: page.getByText('Archived') });

// chaining — scope a search inside another locator
page.getByTestId('sidebar').getByRole('link', { name: 'Settings' });

// positional
page.getByRole('listitem').first();
page.getByRole('listitem').last();
page.getByRole('listitem').nth(2);

// combining locators
page.getByRole('button', { name: 'Save' })
    .or(page.getByRole('button', { name: 'Update' }));

page.getByRole('button').and(page.getByTitle('Submit'));

// count and iterate
const items = page.getByRole('listitem');
const n = await items.count();
for (let i = 0; i < n; i++) {
  console.log(await items.nth(i).textContent());
}

// all() — snapshot into an array
for (const item of await items.all()) {
  console.log(await item.textContent());
}
```

---

## 6. Actions

```typescript
// navigation
await page.goto('/login');
await page.goto('https://example.com', { waitUntil: 'networkidle' });
await page.goBack();
await page.goForward();
await page.reload();

// clicking
await locator.click();
await locator.click({ button: 'right' });
await locator.click({ clickCount: 2 });
await locator.click({ modifiers: ['Control', 'Shift'] });
await locator.click({ position: { x: 10, y: 10 } });
await locator.click({ force: true });            // skip actionability checks
await locator.click({ trial: true });            // check without clicking
await locator.dblclick();

// typing
await locator.fill('text');                      // fast — clears then sets
await locator.clear();
await locator.pressSequentially('slow typing', { delay: 100 });  // real keystrokes
await locator.press('Enter');
await locator.press('Control+A');
await page.keyboard.press('Tab');
await page.keyboard.type('hello');
await page.keyboard.down('Shift');
await page.keyboard.up('Shift');
await page.keyboard.insertText('no key events');

// checkbox / radio
await locator.check();
await locator.uncheck();
await locator.setChecked(true);

// select
await page.selectOption('select#country', 'IN');
await page.selectOption('select#country', { label: 'India' });
await page.selectOption('select#country', { index: 2 });
await page.selectOption('select#multi', ['a', 'b']);

// files
await page.setInputFiles('input[type=file]', 'path/to/file.pdf');
await page.setInputFiles('input[type=file]', ['a.png', 'b.png']);
await page.setInputFiles('input[type=file]', []);    // clear
await page.setInputFiles('input[type=file]', {
  name: 'test.txt',
  mimeType: 'text/plain',
  buffer: Buffer.from('content'),
});

// hover, focus, drag
await locator.hover();
await locator.focus();
await locator.blur();
await locator.dragTo(page.getByTestId('dropzone'));
await page.mouse.move(100, 200);
await page.mouse.down();
await page.mouse.up();
await page.mouse.wheel(0, 500);

// scroll
await locator.scrollIntoViewIfNeeded();

// reading state
await locator.textContent();
await locator.innerText();
await locator.innerHTML();
await locator.inputValue();
await locator.getAttribute('href');
await locator.isVisible();
await locator.isHidden();
await locator.isEnabled();
await locator.isDisabled();
await locator.isChecked();
await locator.isEditable();
await locator.boundingBox();
await locator.screenshot({ path: 'el.png' });
await locator.allTextContents();
await locator.allInnerTexts();
```

---

## 7. Assertions

```typescript
import { expect } from '@playwright/test';

// ---- auto-retrying locator assertions (these WAIT) ----
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeAttached();
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toBeEditable();
await expect(locator).toBeChecked();
await expect(locator).toBeFocused();
await expect(locator).toBeEmpty();
await expect(locator).toBeInViewport();

await expect(locator).toHaveText('exact text');
await expect(locator).toHaveText(/regex/);
await expect(locator).toContainText('partial');
await expect(locator).toHaveValue('input value');
await expect(locator).toHaveValues(['a', 'b']);
await expect(locator).toHaveAttribute('href', '/home');
await expect(locator).toHaveClass(/active/);
await expect(locator).toHaveCount(5);
await expect(locator).toHaveId('main');
await expect(locator).toHaveCSS('display', 'flex');
await expect(locator).toHaveScreenshot('baseline.png');
await expect(locator).toHaveAccessibleName('Submit form');
await expect(locator).toHaveRole('button');

// negation — also retries (waits for it to become false)
await expect(locator).not.toBeVisible();

// custom timeout on a single assertion
await expect(locator).toBeVisible({ timeout: 30_000 });

// ---- page assertions ----
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveURL(/\/dashboard/);
await expect(page).toHaveTitle('Dashboard');
await expect(page).toHaveScreenshot('page.png', { fullPage: true });

// ---- API response assertions ----
await expect(response).toBeOK();

// ---- non-retrying value assertions ----
expect(value).toBe(5);
expect(value).toEqual({ a: 1 });
expect(array).toContain('item');
expect(array).toHaveLength(3);
expect(str).toMatch(/pattern/);
expect(num).toBeGreaterThan(10);
expect(num).toBeCloseTo(3.14, 2);
expect(obj).toHaveProperty('key.nested');
expect(fn).toThrow('error message');
expect(value).toBeTruthy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// ---- soft assertions — collect failures, don't stop the test ----
await expect.soft(locator).toHaveText('a');
await expect.soft(locator2).toHaveText('b');
expect(test.info().errors).toHaveLength(0);      // then check at the end

// ---- poll — retry an arbitrary function ----
await expect.poll(async () => {
  const res = await request.get('/api/status');
  return (await res.json()).state;
}, { timeout: 30_000, intervals: [1000, 2000, 5000] }).toBe('ready');

// ---- toPass — retry a block of assertions ----
await expect(async () => {
  const res = await request.get('/api/job/1');
  expect(res.status()).toBe(200);
  expect((await res.json()).done).toBe(true);
}).toPass({ timeout: 60_000 });
```

**Interview point:** `expect(locator)` auto-retries until the assertion passes or the timeout expires. `expect(value)` does not — it evaluates once. This is why `await expect(locator).toHaveText('x')` is correct and `expect(await locator.textContent()).toBe('x')` is flaky.

---

## 8. Waiting — and what not to do

```typescript
// ❌ never do this
await page.waitForTimeout(5000);           // hard sleep — flaky and slow

// ✅ wait for a condition
await expect(locator).toBeVisible();       // preferred — assertion doubles as a wait
await locator.waitFor({ state: 'visible' });
await locator.waitFor({ state: 'attached' });
await locator.waitFor({ state: 'detached' });
await locator.waitFor({ state: 'hidden' });

await page.waitForURL('**/dashboard');
await page.waitForURL(/\/dashboard/, { timeout: 15_000 });
await page.waitForLoadState('load');
await page.waitForLoadState('domcontentloaded');
await page.waitForLoadState('networkidle');   // use sparingly — often unreliable

await page.waitForResponse('**/api/users');
await page.waitForResponse((r) => r.url().includes('/api/users') && r.status() === 200);
await page.waitForRequest('**/api/**');

await page.waitForFunction(() => document.readyState === 'complete');
await page.waitForFunction(() => (window as any).appReady === true);
await page.waitForSelector('.spinner', { state: 'detached' });

// wait for an event triggered by an action — set up the wait FIRST
const [download] = await Promise.all([
  page.waitForEvent('download'),
  page.getByRole('button', { name: 'Export' }).click(),
]);
await download.saveAs('./downloads/report.csv');

const [popup] = await Promise.all([
  page.waitForEvent('popup'),
  page.getByRole('link', { name: 'Open in new tab' }).click(),
]);
await popup.waitForLoadState();
```

---

## 9. Hooks and test organisation

```typescript
import { test, expect } from '@playwright/test';

test.describe('Checkout', () => {
  test.describe.configure({ mode: 'serial' });   // or 'parallel'

  test.beforeAll(async ({ browser }) => { /* once for the file */ });
  test.afterAll(async () => { /* once for the file */ });
  test.beforeEach(async ({ page }) => { /* before every test */ });
  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status !== testInfo.expectedStatus) {
      await page.screenshot({ path: `failures/${testInfo.title}.png` });
    }
  });

  test('pays with card', async ({ page }) => { /* ... */ });

  test.skip('not implemented yet', async () => {});
  test.fixme('broken, tracked in JIRA-123', async () => {});
  test.only('run just this one', async () => {});          // never commit this
  test.fail('known bug — expected to fail', async () => {});
  test.slow();                                              // triples the timeout

  test('conditional', async ({ page, browserName }) => {
    test.skip(browserName === 'webkit', 'Safari not supported yet');
    test.fixme(process.env.CI === 'true', 'flaky in CI');
  });

  test('annotated', async ({ page }) => {
    test.info().annotations.push({ type: 'issue', description: 'JIRA-456' });
    await test.step('log in', async () => {
      // grouped in the report
    });
    await test.step('add to cart', async () => {});
  });
});

// tags
test('login works @smoke @auth', async () => {});
// npx playwright test --grep "@smoke"
```

---

## 10. Fixtures — the most powerful feature

```typescript
// fixtures.ts
import { test as base, expect, Page } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';

type MyFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  authedPage: Page;
};

type MyWorkerFixtures = {
  apiToken: string;
};

export const test = base.extend<MyFixtures, MyWorkerFixtures>({
  // test-scoped — new for every test
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await use(loginPage);            // test runs here
    // teardown after use()
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  authedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Username').fill(process.env.USER!);
    await page.getByLabel('Password').fill(process.env.PASS!);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('**/dashboard');
    await use(page);
  },

  // worker-scoped — created once per worker process
  apiToken: [async ({}, use) => {
    const token = await fetchToken();
    await use(token);
    await revokeToken(token);
  }, { scope: 'worker' }],

  // auto fixture — runs even if the test doesn't request it
  // (see options below)
});

export { expect };
```

**Using them:**

```typescript
import { test, expect } from './fixtures';

test('dashboard loads after login', async ({ loginPage, dashboardPage }) => {
  await loginPage.login('admin', 'pass');
  await expect(dashboardPage.heading).toBeVisible();
});
```

### Overriding built-in options

```typescript
export const test = base.extend({
  // override an option for all tests in this file
  locale: 'fr-FR',
  viewport: { width: 1920, height: 1080 },
});

// or per-file
test.use({ locale: 'fr-FR', storageState: 'auth/admin.json' });
```

---

## 11. Authentication — do it once, reuse everywhere

```typescript
// global.setup.ts
import { test as setup, expect } from '@playwright/test';

const USER_FILE = 'auth/user.json';
const ADMIN_FILE = 'auth/admin.json';

setup('authenticate as user', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Username').fill(process.env.USER_NAME!);
  await page.getByLabel('Password').fill(process.env.USER_PASS!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: USER_FILE });
});

setup('authenticate as admin', async ({ page }) => {
  // same pattern, different creds, saved to ADMIN_FILE
});
```

```typescript
// playwright.config.ts
projects: [
  { name: 'setup', testMatch: /global\.setup\.ts/ },
  {
    name: 'user-tests',
    use: { ...devices['Desktop Chrome'], storageState: 'auth/user.json' },
    dependencies: ['setup'],
    testMatch: /user\/.*\.spec\.ts/,
  },
  {
    name: 'admin-tests',
    use: { ...devices['Desktop Chrome'], storageState: 'auth/admin.json' },
    dependencies: ['setup'],
    testMatch: /admin\/.*\.spec\.ts/,
  },
]
```

**Faster still — authenticate via API and inject the token:**

```typescript
setup('api login', async ({ request }) => {
  const res = await request.post('/api/auth/login', {
    data: { username: process.env.USER_NAME, password: process.env.USER_PASS },
  });
  const { token } = await res.json();

  await request.storageState({ path: 'auth/api.json' });
  // or inject into localStorage:
  // await page.addInitScript((t) => localStorage.setItem('token', t), token);
});
```

---

## 12. API testing

```typescript
import { test, expect, request } from '@playwright/test';

test('create and fetch a user', async ({ request }) => {
  // POST
  const createRes = await request.post('/api/users', {
    data: { name: 'Alex', email: 'p@example.com' },
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(createRes.ok()).toBeTruthy();
  expect(createRes.status()).toBe(201);

  const created = await createRes.json();
  expect(created).toHaveProperty('id');

  // GET
  const getRes = await request.get(`/api/users/${created.id}`);
  await expect(getRes).toBeOK();
  expect(await getRes.json()).toMatchObject({ name: 'Alex' });

  // PUT / PATCH / DELETE
  await request.put(`/api/users/${created.id}`, { data: { name: 'Updated' } });
  await request.patch(`/api/users/${created.id}`, { data: { age: 31 } });
  const delRes = await request.delete(`/api/users/${created.id}`);
  expect(delRes.status()).toBe(204);

  // other options
  await request.get('/api/search', { params: { q: 'test', page: 1 } });
  await request.post('/api/upload', {
    multipart: { file: { name: 'a.txt', mimeType: 'text/plain', buffer: Buffer.from('x') } },
  });
  await request.post('/api/form', { form: { username: 'a', password: 'b' } });

  // response details
  console.log(getRes.headers());
  console.log(getRes.statusText());
  console.log(await getRes.text());
  console.log(await getRes.body());
});

// standalone context with defaults
const ctx = await request.newContext({
  baseURL: 'https://api.example.com',
  extraHTTPHeaders: { Authorization: `Bearer ${token}` },
  ignoreHTTPSErrors: true,
});
await ctx.dispose();
```

---

## 13. Network interception and mocking

```typescript
// block resources — big speedup
await page.route('**/*.{png,jpg,jpeg,svg,gif,woff2}', (route) => route.abort());
await page.route('**/analytics/**', (route) => route.abort());

// mock a response
await page.route('**/api/users', (route) =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Mocked' }]),
  })
);

// mock from a file
await page.route('**/api/users', (route) => route.fulfill({ path: 'fixtures/users.json' }));

// modify the real response
await page.route('**/api/config', async (route) => {
  const res = await route.fetch();
  const json = await res.json();
  json.featureFlag = true;
  await route.fulfill({ response: res, json });
});

// modify the request
await page.route('**/api/**', (route) =>
  route.continue({ headers: { ...route.request().headers(), 'x-test': '1' } })
);

// simulate errors and delays
await page.route('**/api/slow', async (route) => {
  await new Promise((r) => setTimeout(r, 5000));
  await route.continue();
});
await page.route('**/api/fail', (route) => route.abort('failed'));
await page.route('**/api/500', (route) => route.fulfill({ status: 500 }));

// remove a route
await page.unroute('**/api/users');

// listen without intercepting
page.on('request', (req) => console.log('>>', req.method(), req.url()));
page.on('response', (res) => console.log('<<', res.status(), res.url()));
page.on('requestfailed', (req) => console.log('FAILED', req.url()));
page.on('console', (msg) => console.log('CONSOLE:', msg.type(), msg.text()));
page.on('pageerror', (err) => console.log('PAGE ERROR:', err.message));
page.on('dialog', (dialog) => dialog.accept());

// HAR recording and replay
await page.routeFromHAR('recording.har', { update: true });   // record
await page.routeFromHAR('recording.har', { update: false });  // replay
```

---

## 14. Contexts, tabs, frames, dialogs

```typescript
// multiple isolated users in one test
test('two users chat', async ({ browser }) => {
  const userCtx  = await browser.newContext({ storageState: 'auth/user.json' });
  const adminCtx = await browser.newContext({ storageState: 'auth/admin.json' });

  const userPage  = await userCtx.newPage();
  const adminPage = await adminCtx.newPage();

  await userPage.goto('/chat');
  await adminPage.goto('/chat');

  await userPage.getByPlaceholder('Message').fill('hello');
  await userPage.getByRole('button', { name: 'Send' }).click();

  await expect(adminPage.getByText('hello')).toBeVisible();

  await userCtx.close();
  await adminCtx.close();
});

// iframes
const frame = page.frameLocator('#payment-iframe');
await frame.getByLabel('Card number').fill('4111111111111111');
await frame.frameLocator('#nested').getByRole('button').click();

// dialogs — register the handler BEFORE triggering
page.on('dialog', async (dialog) => {
  console.log(dialog.type(), dialog.message());
  await dialog.accept('prompt answer');
  // await dialog.dismiss();
});
await page.getByRole('button', { name: 'Delete' }).click();

// permissions, geolocation, offline
const ctx = await browser.newContext({
  permissions: ['geolocation', 'clipboard-read'],
  geolocation: { latitude: 12.9716, longitude: 77.5946 },   // Bengaluru
  colorScheme: 'dark',
  offline: false,
});
await ctx.setOffline(true);
await ctx.grantPermissions(['notifications'], { origin: 'https://example.com' });
await ctx.clearCookies();
await ctx.addCookies([{ name: 'session', value: 'abc', domain: 'example.com', path: '/' }]);
```

---

## 15. Visual and accessibility testing

```typescript
// visual regression
await expect(page).toHaveScreenshot('homepage.png');
await expect(page).toHaveScreenshot('homepage.png', {
  fullPage: true,
  maxDiffPixels: 100,
  maxDiffPixelRatio: 0.01,
  threshold: 0.2,
  mask: [page.getByTestId('timestamp'), page.getByTestId('ad-slot')],
  animations: 'disabled',
});
await expect(locator).toHaveScreenshot('button.png');

// update baselines
// npx playwright test --update-snapshots
```

```bash
npm install -D @axe-core/playwright
```

```typescript
import AxeBuilder from '@axe-core/playwright';

test('no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .exclude('#third-party-widget')
    .analyze();

  expect(results.violations).toEqual([]);
});
```

---

## 16. Debugging

```bash
npx playwright test --debug                  # inspector, step through
npx playwright test --ui                     # best DX — time travel, watch mode
PWDEBUG=1 npx playwright test                # same as --debug
DEBUG=pw:api npx playwright test             # verbose API logs
DEBUG=pw:browser* npx playwright test
npx playwright test --headed --workers=1 --timeout=0    # watch it live, no timeout
```

```typescript
await page.pause();                          // breakpoint — opens inspector
console.log(await page.content());           // dump HTML
console.log(await locator.count());
await page.screenshot({ path: 'debug.png', fullPage: true });
```

---

## 17. Environment variables

```bash
npm install -D dotenv
```

```typescript
// playwright.config.ts
import dotenv from 'dotenv';
dotenv.config({ path: `.env.${process.env.NODE_ENV ?? 'dev'}` });
```

```bash
# .env.dev
BASE_URL=https://dev.example.com
USER_NAME=testuser
USER_PASS=secret
```

```bash
# run against different environments
NODE_ENV=staging npx playwright test         # bash
$env:NODE_ENV="staging"; npx playwright test # powershell
```

> Add `.env*` and `auth/*.json` to `.gitignore`. Committing a `storageState` file leaks a live session.

---

## 18. Practice checklist

- [ ] Scaffolded a project and ran tests in all three browsers
- [ ] Used `--ui` mode for a full debugging session
- [ ] Written tests using only role/label/text locators — zero CSS selectors
- [ ] Built a custom fixture that provides a logged-in page object
- [ ] Set up `storageState` auth with a setup project and two roles
- [ ] Mocked an API response and asserted the UI reacted correctly
- [ ] Written an API-only test spec using the `request` fixture
- [ ] Recorded and replayed a trace to debug a failure
- [ ] Added visual regression with masked dynamic regions
- [ ] Sharded a run across 4 workers and merged the reports

---

**Next:** `04-practice-programs.md`
