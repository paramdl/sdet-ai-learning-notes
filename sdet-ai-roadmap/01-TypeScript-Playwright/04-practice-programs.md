# Practice Programs — 40 exercises, easy → hard

> **Rule: write it yourself first.** Give every problem a real attempt before looking anything up. Reading solutions feels productive and teaches nothing.
>
> Track your attempts in a log: `P01 ✅ 12min | P02 ❌ got stuck on generics, retry Sat`

---

## Setup

```bash
mkdir ts-practice && cd ts-practice
npm init -y
npm install -D typescript tsx @types/node
npx tsc --init
mkdir src

# run any file
npx tsx src/p01.ts
```

Turn on `"strict": true` in `tsconfig.json`. No `any` allowed in any solution.

---

# Part A — TypeScript fundamentals (P01–P12)

**P01 — Typed calculator**
Write `add`, `subtract`, `multiply`, `divide`. `divide` must return `number | never` and throw a typed error on divide-by-zero.

**P02 — String utilities**
`reverse`, `isPalindrome`, `capitalise`, `countVowels`, `truncate(str, n)`. All fully typed, no `any`.

**P03 — Array operations without built-ins**
Implement your own `myMap`, `myFilter`, `myReduce`, `myFind` as generic functions. Signatures must match the real ones.

**P04 — Discriminated union**
Model an HTTP result as `{ status: 'success', data: T } | { status: 'error', code: number, message: string } | { status: 'loading' }`. Write a handler with a `switch` and an exhaustiveness check using `never`.

**P05 — Type guards**
Given `unknown` input, write guards `isString`, `isNumberArray`, `isUser` (using `obj is User`). Then write `parseApiResponse(raw: unknown): User` that throws a descriptive error if the shape is wrong.

**P06 — Generic Stack and Queue**
`Stack<T>` with `push`, `pop`, `peek`, `isEmpty`, `size`. `Queue<T>` with `enqueue`, `dequeue`, `front`. Both must be type-safe and return `T | undefined` where appropriate.

**P07 — Generic constraint**
`function pluck<T, K extends keyof T>(items: T[], key: K): T[K][]`. Given an array of users and `"name"`, return `string[]`.

**P08 — Deep readonly**
Write a mapped type `DeepReadonly<T>` that makes every nested property readonly, recursively.

**P09 — Test data factory**
Build `createUser(overrides?: Partial<User>): User` with sensible defaults and a unique auto-incrementing id and email.

**P10 — Retry with backoff**
`retry<T>(fn: () => Promise<T>, attempts: number, baseDelayMs: number): Promise<T>` with exponential backoff. Log each attempt. Rethrow the last error if all attempts fail.

**P11 — Debounce and throttle**
Typed `debounce<F extends (...args: any[]) => void>(fn: F, ms: number): F` and the same for throttle. Preserve the original parameter types.

**P12 — Group and sort**
`groupBy<T, K extends keyof T>(items: T[], key: K): Record<string, T[]>` and `sortBy<T>(items: T[], key: keyof T, dir: 'asc' | 'desc'): T[]`.

---

# Part B — DSA for interviews (P13–P26)

> These are the patterns that actually come up in SDET interviews. Do each in TypeScript, state the time and space complexity in a comment at the top.

**P13 — Two Sum**
Return indices of two numbers summing to a target. O(n) with a hashmap.

**P14 — Valid Anagram**
Two strings, same characters in any order.

**P15 — First non-repeating character**
Return its index, or -1.

**P16 — Longest substring without repeating characters**
Sliding window. Classic.

**P17 — Maximum subarray sum**
Kadane's algorithm.

**P18 — Merge two sorted arrays**
In place if you can, O(n+m).

**P19 — Valid parentheses**
Stack. `"{[()]}"` is valid, `"{[(])}"` is not.

**P20 — Remove duplicates from a sorted array**
In place, return the new length.

**P21 — Binary search**
Iterative and recursive. Then `findFirstOccurrence` in an array with duplicates.

**P22 — Reverse a linked list**
Define the node type yourself. Iterative and recursive.

**P23 — FizzBuzz, typed properly**
Return `("Fizz" | "Buzz" | "FizzBuzz" | number)[]`. Sounds trivial — the typing is the exercise.

**P24 — Flatten a nested array**
`flatten<T>(arr: NestedArray<T>): T[]` where `NestedArray<T> = (T | NestedArray<T>)[]`. Recursive type plus recursive function.

**P25 — Word frequency counter**
Given a paragraph, return the top N words by frequency, ties broken alphabetically.

**P26 — LRU Cache**
`class LRUCache<K, V>` with `get` and `put`, capacity-bounded, O(1) both. Map-based. This one is a genuine interview favourite.

---

# Part C — Playwright fundamentals (P27–P34)

> Target sites that are safe and stable to automate against:
> - `https://playwright.dev`
> - `https://demo.playwright.dev/todomvc`
> - `https://the-internet.herokuapp.com`
> - `https://practice.expandtesting.com`
> - Your own local app

**P27 — First suite**
Scaffold a project. Write 5 tests against `demo.playwright.dev/todomvc`: add a todo, add multiple, mark complete, clear completed, filter by active.
Constraint: role/label/text locators only. Zero CSS selectors.

**P28 — Login flows**
Against `the-internet.herokuapp.com/login`: valid login, invalid password, empty fields, logout. Assert the exact flash message each time.

**P29 — Table handling**
Find a data table. Write helpers: `getRowCount()`, `getCellValue(row, col)`, `findRowByText(text)`, `sortByColumn(name)`, `getColumnValues(name)`. Assert sorting actually worked.

**P30 — Dynamic waits**
Find a page with a loading spinner and a delayed element. Handle it correctly with no `waitForTimeout` anywhere. Prove it by running 10 times with `--repeat-each=10` and getting 10 passes.

**P31 — File upload and download**
Upload a file and assert the success state. Trigger a download and assert the file exists on disk with non-zero size.

**P32 — Frames and dialogs**
Handle an iframe, a JS alert, a confirm, and a prompt. Register handlers correctly.

**P33 — API tests**
Using `request`: full CRUD against a public API (`https://reqres.in` or `jsonplaceholder.typicode.com`). Assert status codes, response shape, and headers. Include one negative test per endpoint.

**P34 — Network mocking**
Take any test from P27. Mock the API so the list returns 3 fixed items. Then mock a 500 and assert the UI shows an error state. Then block all images and measure the speed difference.

---

# Part D — Framework building (P35–P40)

**P35 — Page Object Model from scratch**
Build `BasePage` (abstract), three page objects, and rewrite P28's tests to use them. Locators must be private.

**P36 — Component objects**
Extract `TableComponent`, `ModalComponent`, `NavComponent`. Compose them into a page object. Prove reuse by using `TableComponent` on two different pages.

**P37 — Custom fixtures**
Build fixtures providing: an authenticated page, each page object, and a worker-scoped API token. Rewrite your tests to consume them. No `new LoginPage(page)` should remain in any spec file.

**P38 — Data-driven tests**
Read test cases from a JSON and a CSV file. Generate tests in a loop. Each case gets a distinct, readable test title.

**P39 — Multi-environment config**
Support dev/staging/prod via `.env` files and a `NODE_ENV` switch. Add projects for chromium, firefox, and mobile. Make `npm run test:staging:mobile` work.

**P40 — The full harness**
Combine everything: POM + components + fixtures + data-driven + multi-env + HTML/JUnit reporters + trace on failure + retry config + sharding. This becomes the base for your capstone.

---

# Solutions — selected

> Only three are given. The rest you write. If you're truly stuck on one for more than 45 minutes, look up the *concept*, not the answer.

### P06 — Generic Stack

```typescript
export class Stack<T> {
  private readonly items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  get size(): number {
    return this.items.length;
  }

  toArray(): readonly T[] {
    return [...this.items];
  }
}

// usage
const s = new Stack<number>();
s.push(1);
s.push(2);
console.log(s.pop());   // 2
console.log(s.peek());  // 1
```

### P08 — DeepReadonly

```typescript
type DeepReadonly<T> = T extends (infer R)[]
  ? ReadonlyArray<DeepReadonly<R>>
  : T extends Function
  ? T
  : T extends object
  ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
  : T;

interface Config {
  db: { host: string; ports: number[] };
  debug: boolean;
}

const c: DeepReadonly<Config> = {
  db: { host: 'localhost', ports: [5432] },
  debug: true,
};

// c.db.host = 'x';      // ❌ readonly
// c.db.ports.push(1);   // ❌ ReadonlyArray
```

### P26 — LRU Cache

```typescript
export class LRUCache<K, V> {
  private readonly cache = new Map<K, V>();

  constructor(private readonly capacity: number) {
    if (capacity <= 0) throw new Error('Capacity must be positive');
  }

  get(key: K): V | undefined {
    if (!this.cache.has(key)) return undefined;

    // touch — delete and re-set moves it to the end (most recent)
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  put(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.capacity) {
      // Map preserves insertion order — first key is least recently used
      const lru = this.cache.keys().next().value as K;
      this.cache.delete(lru);
    }
    this.cache.set(key, value);
  }

  get size(): number {
    return this.cache.size;
  }
}

// Time: O(1) get and put. Space: O(capacity).
// The trick is that JS Map guarantees insertion order,
// so delete+set is an O(1) "move to most recent".
```

---

## Weekly targets

| Week | Programs | Hours |
|---|---|---|
| 1 | P01–P06 | ~15 |
| 2 | P07–P12 | ~15 |
| 3 | P13–P20 | ~17 |
| 4 | P21–P26, P27–P28 | ~17 |
| 5 | P29–P34 | ~17 |
| 6 | P35–P37 | ~17 |
| 7 | P38–P40 | ~17 |

Keep going with DSA at ~30 min/day past week 4 — 120 problems total by week 13 is the goal. Consistency beats intensity here.

---

**Next:** `05-interview-questions.md`
