# OOP Concepts — with Real Playwright Examples

> Every OOP concept below is shown twice: the textbook definition (for the interview answer) and the real test-framework code (for the follow-up question "where have you actually used this?").
>
> That second half is what separates a candidate who memorised definitions from one who has built something.

---

## The four pillars — quick reference

| Pillar | One-line definition | Where it shows up in a test framework |
|---|---|---|
| **Encapsulation** | Bundle data with the methods that operate on it; hide internals | Locators are `private`; tests only call public actions |
| **Inheritance** | A class acquires properties and behaviour from a parent | `BasePage` → `LoginPage`, `DashboardPage` |
| **Polymorphism** | One interface, many implementations, resolved at runtime | `PaymentMethod` with Card / UPI / Wallet variants |
| **Abstraction** | Expose *what* it does, hide *how* | `abstract class BasePage` defines the contract |

---

## 1. Class basics and access modifiers

```typescript
import { Page, Locator } from '@playwright/test';

class LoginPage {
  // public    — accessible everywhere (default)
  // private   — only inside this class
  // protected — inside this class and subclasses
  // readonly  — cannot be reassigned after the constructor

  public readonly url: string = '/login';

  private readonly usernameInput: Locator;
  private readonly passwordInput: Locator;
  private readonly submitButton: Locator;
  private readonly errorMessage: Locator;

  protected readonly page: Page;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton  = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage  = page.getByTestId('login-error');
  }

  async goto(): Promise<void> {
    await this.page.goto(this.url);
  }

  async login(username: string, password: string): Promise<void> {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorText(): Promise<string> {
    return (await this.errorMessage.textContent()) ?? '';
  }
}
```

### Parameter properties — the shorthand

```typescript
class LoginPage {
  // declares AND assigns this.page in one line
  constructor(private readonly page: Page) {}
}
```

### Why `private` on locators matters

```typescript
// ❌ Without encapsulation — the test knows the DOM
test('bad', async ({ page }) => {
  await page.locator('#username').fill('admin');
  await page.locator('#password').fill('pass');
  await page.locator('#submit').click();
});
// When #username becomes #user-name, you edit 40 test files.

// ✅ With encapsulation — the test knows only intent
test('good', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin', 'pass');
});
// When the selector changes, you edit one line in one file.
```

**Interview answer:** "Encapsulation in my framework means locators are private fields on the page object. Tests can't reach the DOM directly — they call intent-revealing methods like `login()`. The payoff is that a selector change touches exactly one file instead of every test that used it."

---

## 2. Abstraction — `abstract class`

An abstract class cannot be instantiated. It defines a contract subclasses must fulfil, while providing shared behaviour.

```typescript
import { Page, Locator, expect } from '@playwright/test';

abstract class BasePage {
  protected constructor(protected readonly page: Page) {}

  // abstract — every subclass MUST implement these
  abstract get path(): string;
  abstract get uniqueElement(): Locator;

  // concrete — shared by all subclasses
  async goto(): Promise<void> {
    await this.page.goto(this.path);
    await this.waitUntilLoaded();
  }

  async waitUntilLoaded(): Promise<void> {
    await expect(this.uniqueElement).toBeVisible({ timeout: 15_000 });
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }

  async screenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
  }

  protected async dismissCookieBannerIfPresent(): Promise<void> {
    const banner = this.page.getByRole('button', { name: /accept/i });
    if (await banner.isVisible().catch(() => false)) {
      await banner.click();
    }
  }
}

// ❌ const p = new BasePage(page);   // Error: cannot instantiate abstract class

class DashboardPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get path(): string {
    return '/dashboard';
  }

  get uniqueElement(): Locator {
    return this.page.getByRole('heading', { name: 'Dashboard' });
  }

  async getWidgetCount(): Promise<number> {
    return this.page.getByTestId('widget').count();
  }
}
```

**Interview answer:** "`BasePage` is abstract because it's never a real page — it's a contract. It forces every page object to declare its path and a unique element, which is what my generic `waitUntilLoaded()` relies on. Shared behaviour like screenshots and cookie-banner dismissal lives there so it isn't duplicated 30 times."

---

## 3. Inheritance

```typescript
class BasePage {
  constructor(protected readonly page: Page) {}
  async goto(path: string) { await this.page.goto(path); }
  async reload() { await this.page.reload(); }
}

class AuthenticatedPage extends BasePage {
  protected readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);                           // must call before using `this`
    this.logoutButton = page.getByRole('button', { name: 'Log out' });
  }

  async logout(): Promise<void> {
    await this.logoutButton.click();
    await this.page.waitForURL('**/login');
  }
}

class ProfilePage extends AuthenticatedPage {
  private readonly nameField: Locator;

  constructor(page: Page) {
    super(page);
    this.nameField = page.getByLabel('Display name');
  }

  async updateName(name: string): Promise<void> {
    await this.nameField.fill(name);
    await this.page.getByRole('button', { name: 'Save' }).click();
  }
}

// ProfilePage inherits logout() from AuthenticatedPage
// and goto()/reload() from BasePage
```

### Method overriding + `super`

```typescript
class BasePage {
  async goto(path: string): Promise<void> {
    await this.page.goto(path);
  }
}

class SlowLoadingPage extends BasePage {
  override async goto(path: string): Promise<void> {
    await super.goto(path);                              // reuse parent behaviour
    await this.page.waitForLoadState('networkidle');     // then add our own
    await this.page.waitForSelector('.spinner', { state: 'detached' });
  }
}
```

> Use the `override` keyword. With `noImplicitOverride: true` in tsconfig, TypeScript will error if you *think* you're overriding but misspelled the method name — a real bug this catches.

### The inheritance trap

**Do not build deep hierarchies.** Three levels is already a smell.

```
BasePage → AuthenticatedPage → AdminPage → AdminUserPage → AdminUserEditPage   ❌
```

When you need behaviour from two unrelated places, use **composition** (section 6), not another inheritance level.

---

## 4. Polymorphism

Same call, different behaviour, decided at runtime.

```typescript
interface PaymentMethod {
  readonly name: string;
  pay(amount: number): Promise<void>;
  isAvailable(): Promise<boolean>;
}

class CardPayment implements PaymentMethod {
  readonly name = 'Card';
  constructor(private readonly page: Page) {}

  async isAvailable(): Promise<boolean> {
    return this.page.getByTestId('pay-card').isVisible();
  }

  async pay(amount: number): Promise<void> {
    await this.page.getByTestId('pay-card').click();
    await this.page.getByLabel('Card number').fill('4111111111111111');
    await this.page.getByLabel('Expiry').fill('12/30');
    await this.page.getByLabel('CVV').fill('123');
    await this.page.getByRole('button', { name: `Pay ₹${amount}` }).click();
  }
}

class UpiPayment implements PaymentMethod {
  readonly name = 'UPI';
  constructor(private readonly page: Page) {}

  async isAvailable(): Promise<boolean> {
    return this.page.getByTestId('pay-upi').isVisible();
  }

  async pay(amount: number): Promise<void> {
    await this.page.getByTestId('pay-upi').click();
    await this.page.getByLabel('UPI ID').fill('test@okbank');
    await this.page.getByRole('button', { name: 'Verify and pay' }).click();
  }
}

class WalletPayment implements PaymentMethod {
  readonly name = 'Wallet';
  constructor(private readonly page: Page) {}

  async isAvailable(): Promise<boolean> {
    const balance = await this.page.getByTestId('wallet-balance').textContent();
    return parseFloat(balance ?? '0') > 0;
  }

  async pay(amount: number): Promise<void> {
    await this.page.getByTestId('pay-wallet').click();
    await this.page.getByRole('button', { name: 'Confirm' }).click();
  }
}
```

**The test doesn't care which one it got:**

```typescript
const methods: PaymentMethod[] = [
  new CardPayment(page),
  new UpiPayment(page),
  new WalletPayment(page),
];

for (const method of methods) {
  test(`checkout with ${method.name}`, async ({ page }) => {
    await checkoutPage.goto();
    if (!(await method.isAvailable())) test.skip();

    await method.pay(499);                              // ← polymorphic call

    await expect(page.getByText('Order confirmed')).toBeVisible();
  });
}
```

**Interview answer:** "I used polymorphism for payment testing on a creator platform. Card, UPI, and wallet all implement a `PaymentMethod` interface with `pay()` and `isAvailable()`. The checkout test loops over the array and calls `pay()` — it has no idea which implementation it's holding. Adding a new payment method means writing one class, not touching any test."

### Two kinds of polymorphism

```typescript
// Runtime polymorphism (overriding) — shown above

// Compile-time polymorphism (overloading)
class ElementFinder {
  find(id: number): Locator;
  find(testId: string): Locator;
  find(selector: { role: string; name: string }): Locator;
  find(arg: number | string | { role: string; name: string }): Locator {
    if (typeof arg === 'number') return this.page.getByTestId(`item-${arg}`);
    if (typeof arg === 'string') return this.page.getByTestId(arg);
    return this.page.getByRole(arg.role as any, { name: arg.name });
  }
}
```

---

## 5. Interfaces vs abstract classes

```typescript
interface Reportable {
  generateReport(): Promise<string>;
}

interface Screenshotable {
  capture(name: string): Promise<Buffer>;
}

// a class can implement MANY interfaces
// but can extend only ONE class
class TestRunner extends BaseRunner implements Reportable, Screenshotable {
  async generateReport(): Promise<string> { return 'report'; }
  async capture(name: string): Promise<Buffer> { return Buffer.from(''); }
}
```

| | `interface` | `abstract class` |
|---|---|---|
| Implementation code | No | Yes — can have concrete methods |
| Fields with values | No | Yes |
| Constructor | No | Yes |
| Multiple per class | Yes (`implements A, B, C`) | No (`extends` one only) |
| Exists at runtime | No — erased | Yes |

**Rule of thumb:** interface when you only need a contract; abstract class when subclasses should also share real code.

---

## 6. Composition over inheritance

The most important practical lesson in this file.

```typescript
// ❌ Inheritance forces a single chain and gets stuck
class BasePage {}
class PageWithTable extends BasePage {}
class PageWithModal extends BasePage {}
// Now you need a page with BOTH a table and a modal. Stuck.

// ✅ Composition — assemble behaviour from parts
class TableComponent {
  constructor(private readonly root: Locator) {}

  async rowCount(): Promise<number> {
    return this.root.locator('tbody tr').count();
  }

  async getCell(row: number, col: number): Promise<string> {
    return (
      (await this.root.locator('tbody tr').nth(row).locator('td').nth(col).textContent()) ?? ''
    );
  }

  async sortBy(column: string): Promise<void> {
    await this.root.getByRole('columnheader', { name: column }).click();
  }
}

class ModalComponent {
  constructor(private readonly root: Locator) {}

  async confirm(): Promise<void> {
    await this.root.getByRole('button', { name: 'Confirm' }).click();
  }

  async cancel(): Promise<void> {
    await this.root.getByRole('button', { name: 'Cancel' }).click();
  }

  async isOpen(): Promise<boolean> {
    return this.root.isVisible();
  }
}

class SearchComponent {
  constructor(private readonly root: Locator) {}

  async search(term: string): Promise<void> {
    await this.root.getByPlaceholder('Search').fill(term);
    await this.root.getByPlaceholder('Search').press('Enter');
  }
}

// Now assemble freely — take exactly what this page needs
class UsersAdminPage extends BasePage {
  readonly table: TableComponent;
  readonly deleteModal: ModalComponent;
  readonly search: SearchComponent;

  constructor(page: Page) {
    super(page);
    this.table       = new TableComponent(page.getByTestId('users-table'));
    this.deleteModal = new ModalComponent(page.getByRole('dialog'));
    this.search      = new SearchComponent(page.getByTestId('toolbar'));
  }

  async deleteUser(name: string): Promise<void> {
    await this.search.search(name);
    await this.page.getByRole('row', { name }).getByRole('button', { name: 'Delete' }).click();
    await this.deleteModal.confirm();
  }
}
```

**Usage reads beautifully:**

```typescript
const usersPage = new UsersAdminPage(page);
await usersPage.goto();
await usersPage.search.search('alex');
expect(await usersPage.table.rowCount()).toBe(1);
await usersPage.deleteUser('alex');
expect(await usersPage.deleteModal.isOpen()).toBe(false);
```

**Interview answer:** "I prefer composition. In my framework, tables, modals, and search bars are components scoped to a root locator, and page objects hold them as fields. Inheritance would force every page into one chain — composition lets a page take exactly the parts it has. It's also easier to test the components in isolation."

---

## 7. `static` members

```typescript
class TestDataFactory {
  private static counter = 0;

  // no instance needed — TestDataFactory.uniqueEmail()
  static uniqueEmail(): string {
    return `test+${Date.now()}_${++this.counter}@example.com`;
  }

  static buildUser(overrides: Partial<User> = {}): User {
    return {
      id: this.counter++,
      name: `User ${this.counter}`,
      email: this.uniqueEmail(),
      age: 30,
      ...overrides,
    };
  }
}

const u = TestDataFactory.buildUser({ name: 'Admin' });
```

### Singleton — one shared instance

```typescript
class ConfigManager {
  private static instance: ConfigManager;
  private readonly settings: Map<string, string> = new Map();

  private constructor() {                       // private — blocks `new`
    this.settings.set('baseUrl', process.env.BASE_URL ?? 'http://localhost:3000');
    this.settings.set('timeout', process.env.TIMEOUT ?? '30000');
  }

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  get(key: string): string {
    const value = this.settings.get(key);
    if (!value) throw new Error(`Missing config: ${key}`);
    return value;
  }
}

const baseUrl = ConfigManager.getInstance().get('baseUrl');
```

> **Caution for the interview:** singletons and parallel test execution fight each other. If you mention singleton, be ready for "how does that behave across parallel workers?" The honest answer: each Playwright worker is a separate Node process, so each gets its own instance — which is fine for read-only config, and dangerous for anything mutable like shared test data.

---

## 8. Getters and setters

```typescript
class CartPage extends BasePage {
  private _itemCount = 0;

  get itemCount(): number {
    return this._itemCount;
  }

  set itemCount(value: number) {
    if (value < 0) throw new Error('Item count cannot be negative');
    this._itemCount = value;
  }

  // computed getter — no backing field
  get isEmpty(): boolean {
    return this._itemCount === 0;
  }

  // lazily built locator — evaluated fresh each access
  get checkoutButton(): Locator {
    return this.page.getByRole('button', { name: 'Checkout' });
  }
}

const cart = new CartPage(page);
cart.itemCount = 5;            // calls the setter
console.log(cart.itemCount);   // calls the getter
console.log(cart.isEmpty);     // false
```

**Why getters for locators:** a getter re-evaluates every time you touch it. If the page re-renders, a locator built in the constructor may point at a detached element, while a getter always gives you a fresh one.

---

## 9. SOLID — the short version with test examples

| Principle | Meaning | In your framework |
|---|---|---|
| **S**ingle Responsibility | A class has one reason to change | `LoginPage` handles login. It does not also send API requests or read test data. |
| **O**pen/Closed | Open to extension, closed to modification | Add `NetBankingPayment` by writing a new class — never by editing existing ones. |
| **L**iskov Substitution | A subclass must work anywhere the parent works | Any `BasePage` subclass must be safe to pass to a helper that calls `goto()`. |
| **I**nterface Segregation | Many small interfaces beat one fat one | `Reportable` and `Screenshotable` separately, not one `ITestUtils` with 20 methods. |
| **D**ependency Inversion | Depend on abstractions, not concretions | Tests depend on the `PaymentMethod` interface, not on `CardPayment`. |

### Single Responsibility, shown

```typescript
// ❌ This class has three reasons to change
class LoginPage {
  async login() {}
  async createUserViaApi() {}     // API concern
  async readUsersFromCsv() {}     // test-data concern
  async sendSlackAlert() {}       // reporting concern
}

// ✅ Split by responsibility
class LoginPage      { async login() {} }
class UserApiClient  { async createUser() {} }
class CsvDataReader  { async read() {} }
class SlackNotifier  { async notify() {} }
```

---

## 10. Design patterns that actually appear in test frameworks

### Page Object Model — you know this one

Already shown throughout this file.

### Factory

```typescript
type PageName = 'login' | 'dashboard' | 'profile' | 'users';

class PageFactory {
  static create(name: PageName, page: Page): BasePage {
    switch (name) {
      case 'login':     return new LoginPage(page);
      case 'dashboard': return new DashboardPage(page);
      case 'profile':   return new ProfilePage(page);
      case 'users':     return new UsersAdminPage(page);
      default: {
        const _exhaustive: never = name;
        throw new Error(`Unknown page: ${_exhaustive}`);
      }
    }
  }
}
```

### Builder — for complex test data

```typescript
class UserBuilder {
  private user: User = {
    id: 0,
    name: 'Default',
    email: 'default@example.com',
    age: 25,
  };

  withName(name: string): this { this.user.name = name; return this; }
  withEmail(email: string): this { this.user.email = email; return this; }
  withAge(age: number): this { this.user.age = age; return this; }
  asAdmin(): this { this.user.name = `Admin ${this.user.name}`; return this; }

  build(): User { return { ...this.user }; }
}

const admin = new UserBuilder()
  .withName('Alex')
  .withEmail('p@example.com')
  .asAdmin()
  .build();
```

> Returning `this` is what enables the chaining. Type it as `this`, not as `UserBuilder`, so subclasses chain correctly too.

### Fluent page objects

```typescript
class LoginPage extends BasePage {
  async enterUsername(u: string): Promise<this> {
    await this.usernameInput.fill(u);
    return this;
  }

  async enterPassword(p: string): Promise<this> {
    await this.passwordInput.fill(p);
    return this;
  }

  async submit(): Promise<DashboardPage> {
    await this.submitButton.click();
    return new DashboardPage(this.page);     // returns the NEXT page
  }
}

// reads like the user journey
const dashboard = await (await (await loginPage
  .enterUsername('admin'))
  .enterPassword('pass'))
  .submit();
```

> Honest note: fluent chaining with `await` in TypeScript is ugly because every step returns a Promise. Plenty of teams skip it for that reason. Know it, mention the trade-off, don't force it.

---

## 11. Full worked example — a complete mini framework

```typescript
// ---------- src/pages/BasePage.ts ----------
import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  protected constructor(protected readonly page: Page) {}

  abstract get path(): string;
  abstract get uniqueElement(): Locator;

  async goto(): Promise<void> {
    await this.page.goto(this.path);
    await expect(this.uniqueElement).toBeVisible({ timeout: 15_000 });
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }
}

// ---------- src/components/TableComponent.ts ----------
import { Locator } from '@playwright/test';

export class TableComponent {
  constructor(private readonly root: Locator) {}

  async rowCount(): Promise<number> {
    return this.root.locator('tbody tr').count();
  }

  async rowByText(text: string): Promise<Locator> {
    return this.root.getByRole('row', { name: text });
  }
}

// ---------- src/pages/UsersPage.ts ----------
import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';
import { TableComponent } from '../components/TableComponent';

export class UsersPage extends BasePage {
  readonly table: TableComponent;

  constructor(page: Page) {
    super(page);
    this.table = new TableComponent(page.getByTestId('users-table'));
  }

  get path(): string { return '/admin/users'; }
  get uniqueElement(): Locator {
    return this.page.getByRole('heading', { name: 'Users' });
  }

  async deleteUser(name: string): Promise<void> {
    const row = await this.table.rowByText(name);
    await row.getByRole('button', { name: 'Delete' }).click();
    await this.page.getByRole('dialog').getByRole('button', { name: 'Confirm' }).click();
  }
}

// ---------- tests/users.spec.ts ----------
import { test, expect } from '@playwright/test';
import { UsersPage } from '../src/pages/UsersPage';

test.describe('Users admin', () => {
  let usersPage: UsersPage;

  test.beforeEach(async ({ page }) => {
    usersPage = new UsersPage(page);
    await usersPage.goto();
  });

  test('deleting a user removes the row', async () => {
    const before = await usersPage.table.rowCount();

    await usersPage.deleteUser('alex');

    expect(await usersPage.table.rowCount()).toBe(before - 1);
  });
});
```

---

## 12. OOP interview questions — with answers

**Q: What are the four pillars of OOP?**
Encapsulation, inheritance, polymorphism, abstraction. Give the definition, then immediately give your framework example — that's what lands.

**Q: Difference between abstraction and encapsulation?**
Abstraction is about *design* — deciding what to expose. Encapsulation is about *implementation* — enforcing that hiding with access modifiers. `BasePage` being abstract is abstraction; locators being `private` is encapsulation.

**Q: Can you instantiate an abstract class?**
No. It's a contract with partial implementation. Instantiate a concrete subclass.

**Q: Interface vs abstract class — when do you pick which?**
Interface when you only need a contract and a class may need several. Abstract class when subclasses should inherit real shared code. A class implements many interfaces but extends only one class.

**Q: What is method overriding vs overloading?**
Overriding is runtime — a subclass replaces a parent method with the same signature. Overloading is compile-time — multiple signatures for one implementation. TypeScript supports overload signatures but only one implementation body.

**Q: Why composition over inheritance?**
Inheritance forces a single chain and gets stuck when a class needs behaviour from two unrelated places. Composition lets you assemble exactly what you need, is easier to test in isolation, and avoids fragile base-class problems. My page objects hold component objects rather than inheriting from a deep hierarchy.

**Q: What is the Liskov Substitution Principle, in test terms?**
Any subclass must be safe to use wherever the parent is expected. If a helper takes a `BasePage` and calls `goto()`, every subclass's `goto()` must behave sanely — not throw, not require extra setup the helper doesn't know about.

**Q: How do you avoid the Page Object anti-pattern of god classes?**
Single Responsibility. If a page object starts making API calls or reading CSVs, those move to separate classes. And large pages get broken into components scoped to a root locator.

**Q: Is the singleton pattern safe in parallel test runs?**
Each Playwright worker is a separate Node process, so each gets its own instance. Read-only config is fine. Anything mutable and shared — a counter, a cached token, a data pool — becomes a race condition or a silent duplication bug across workers.

**Q: What does `super` do?**
Calls the parent constructor or a parent method. In a subclass constructor you must call `super()` before touching `this`.

**Q: What are access modifiers and why use them in a test framework?**
`public`, `private`, `protected`, plus `readonly`. In a framework, `private` on locators stops tests reaching the DOM, `protected` shares helpers with subclasses without exposing them to tests, and `readonly` prevents accidental reassignment of a page or locator.

---

## 13. Practice checklist

Write these from scratch:

- [ ] `abstract class BasePage` with two abstract members and three concrete methods
- [ ] Three page objects extending it, all with private locators
- [ ] A `TableComponent` and a `ModalComponent` scoped to a root locator
- [ ] A page object that **composes** both components
- [ ] An interface with three implementations, looped over polymorphically
- [ ] A `UserBuilder` with a fluent chaining API
- [ ] A `PageFactory` with an exhaustiveness check in the default branch
- [ ] A static `TestDataFactory` producing unique emails
- [ ] Refactor one of your existing real projects (`QA-Framework-Template`) to use composition

---

**Next:** `03-playwright-commands.md`
