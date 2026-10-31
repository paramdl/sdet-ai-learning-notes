# TypeScript Core — for SDETs

> Goal: write TypeScript that a developer would approve in code review. Not "JavaScript with a few types sprinkled on."

---

## 1. Setup commands

```bash
# new project
mkdir ts-practice && cd ts-practice
npm init -y

# typescript toolchain
npm install -D typescript @types/node ts-node tsx
npx tsc --init

# run a single file (fastest loop for practice)
npx tsx src/day01.ts

# watch mode
npx tsx watch src/day01.ts

# compile everything
npx tsc

# compile + watch
npx tsc --watch

# type-check only, no output files
npx tsc --noEmit
```

### `tsconfig.json` worth using

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022", "DOM"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

**`strict: true` is non-negotiable.** Every interview-grade TS codebase runs strict. Learning without it teaches you bad habits you'll have to unlearn.

---

## 2. Types — the foundation

```typescript
// primitives
let name: string = "Alex";
let age: number = 30;
let isActive: boolean = true;
let nothing: null = null;
let notSet: undefined = undefined;
let big: bigint = 100n;
let sym: symbol = Symbol("id");

// arrays — two equivalent syntaxes
let scores: number[] = [1, 2, 3];
let names: Array<string> = ["a", "b"];

// tuple — fixed length, fixed types per position
let pair: [string, number] = ["age", 30];
let httpResult: [number, string] = [200, "OK"];

// readonly tuple
const point: readonly [number, number] = [10, 20];

// any — avoid. it disables type checking entirely
let loose: any = "anything";

// unknown — the safe version of any. must narrow before use
let safe: unknown = fetchSomething();
if (typeof safe === "string") {
  console.log(safe.toUpperCase()); // OK — narrowed
}

// never — a value that can never occur
function fail(msg: string): never {
  throw new Error(msg);
}

// void — function returns nothing
function log(msg: string): void {
  console.log(msg);
}
```

### `any` vs `unknown` — a guaranteed interview question

| | `any` | `unknown` |
|---|---|---|
| Assign anything to it | Yes | Yes |
| Assign it to anything else | Yes | No |
| Call methods on it | Yes (unchecked) | No — must narrow first |
| Type safety | Off | On |

**Answer to give:** "`any` opts out of the type system — it's an escape hatch that silently spreads. `unknown` is the type-safe counterpart: you can receive anything, but you must prove what it is before you use it. I use `unknown` for API responses and narrow with a type guard."

---

## 3. Interfaces vs Type aliases

```typescript
// interface — describes object shape, can be extended and merged
interface User {
  id: number;
  name: string;
  email?: string;           // optional
  readonly createdAt: Date;  // cannot reassign after creation
}

interface AdminUser extends User {
  permissions: string[];
}

// declaration merging — interfaces only
interface User {
  lastLogin?: Date;   // merges into the User above
}

// type alias — can describe anything, not just objects
type ID = string | number;
type Status = "pending" | "active" | "suspended";
type Callback = (err: Error | null, data?: string) => void;
type Point = { x: number; y: number };

// intersection
type Employee = User & { salary: number; department: string };

// type alias cannot be reopened — this is an error:
// type ID = boolean;   // ❌ Duplicate identifier
```

### When to use which

| Use | For |
|---|---|
| `interface` | Object shapes, class contracts, anything public that might be extended |
| `type` | Unions, intersections, function types, mapped/conditional types, tuples |

**Answer to give:** "I default to `interface` for object shapes because it extends cleanly and supports declaration merging, which matters for augmenting third-party types — like extending Playwright's fixtures. I use `type` when I need a union, a function signature, or anything computed with mapped or conditional types."

---

## 4. Union, intersection, narrowing

```typescript
type Result = { ok: true; data: string } | { ok: false; error: string };

function handle(r: Result) {
  // discriminated union — TS narrows on the `ok` literal
  if (r.ok) {
    console.log(r.data);    // TS knows data exists
  } else {
    console.log(r.error);   // TS knows error exists
  }
}

// narrowing techniques
function process(value: string | number | string[] | Date | null) {
  if (value === null) return "null";
  if (typeof value === "string") return value.toUpperCase();   // typeof
  if (typeof value === "number") return value.toFixed(2);
  if (Array.isArray(value)) return value.join(",");            // Array.isArray
  if (value instanceof Date) return value.toISOString();       // instanceof
  return "unreachable";
}

// `in` operator narrowing
type Dog = { bark(): void };
type Cat = { meow(): void };
function speak(pet: Dog | Cat) {
  if ("bark" in pet) pet.bark();
  else pet.meow();
}

// custom type guard — the `is` keyword
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "name" in obj
  );
}

const data: unknown = await res.json();
if (isUser(data)) {
  console.log(data.name);   // safely narrowed to User
}
```

**Exhaustiveness checking** — catches missed cases at compile time:

```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number }
  | { kind: "rect"; w: number; h: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "square": return s.side ** 2;
    case "rect":   return s.w * s.h;
    default:
      const _exhaustive: never = s;   // compile error if a case is missing
      return _exhaustive;
  }
}
```

---

## 5. Functions

```typescript
// basic
function add(a: number, b: number): number {
  return a + b;
}

// arrow
const multiply = (a: number, b: number): number => a * b;

// optional + default params
function greet(name: string, greeting: string = "Hello", title?: string): string {
  return `${greeting}, ${title ?? ""} ${name}`.trim();
}

// rest params
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

// function type alias
type Validator = (input: string) => boolean;
const isEmail: Validator = (s) => /\S+@\S+\.\S+/.test(s);

// overloads
function parse(input: string): object;
function parse(input: string, raw: true): string;
function parse(input: string, raw?: boolean): object | string {
  return raw ? input : JSON.parse(input);
}
```

---

## 6. Generics — where most people stall

```typescript
// the problem generics solve
function firstBad(arr: any[]): any { return arr[0]; }        // loses type
function first<T>(arr: T[]): T | undefined { return arr[0]; } // keeps type

const n = first([1, 2, 3]);        // number | undefined
const s = first(["a", "b"]);       // string | undefined

// multiple type params
function pair<K, V>(key: K, value: V): [K, V] {
  return [key, value];
}

// constraints — T must have a length property
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
longest("hello", "hi");        // OK
longest([1, 2], [1, 2, 3]);    // OK
// longest(10, 20);            // ❌ number has no length

// keyof — constrain to keys of an object
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
const user = { id: 1, name: "P" };
getProp(user, "name");    // string
// getProp(user, "xyz");  // ❌ not a key of user

// generic interface
interface ApiResponse<T> {
  status: number;
  data: T;
  error?: string;
}
type UserResponse = ApiResponse<User>;
type UserListResponse = ApiResponse<User[]>;

// generic class
class Repository<T extends { id: number }> {
  private items: T[] = [];
  add(item: T): void { this.items.push(item); }
  findById(id: number): T | undefined {
    return this.items.find((i) => i.id === id);
  }
  getAll(): readonly T[] { return this.items; }
}

const userRepo = new Repository<User>();

// default type param
interface Box<T = string> { value: T; }
const b1: Box = { value: "hi" };        // T defaults to string
const b2: Box<number> = { value: 42 };
```

### Real SDET use: a typed API client

```typescript
async function apiGet<T>(url: string): Promise<ApiResponse<T>> {
  const res = await fetch(url);
  const body = (await res.json()) as T;
  return { status: res.status, data: body };
}

// caller gets full type safety
const { data } = await apiGet<User[]>("/api/users");
data.forEach((u) => console.log(u.name));   // u is User
```

---

## 7. Utility types — memorise these

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

Partial<User>              // all props optional  { id?, name?, email?, age? }
Required<User>             // all props required
Readonly<User>             // all props readonly
Pick<User, "id" | "name">  // { id, name }
Omit<User, "email">        // { id, name, age }
Record<string, number>     // { [key: string]: number }
Exclude<"a"|"b"|"c", "a">  // "b" | "c"
Extract<"a"|"b", "a"|"z">  // "a"
NonNullable<string | null> // string
ReturnType<typeof add>     // number
Parameters<typeof add>     // [number, number]
Awaited<Promise<string>>   // string
```

**Real use in test code:**

```typescript
// a test factory that lets you override any field
function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: 1,
    name: "Test User",
    email: "test@example.com",
    age: 30,
    ...overrides,
  };
}

const admin = buildUser({ name: "Admin", age: 45 });

// config where every env must be present
type Env = "dev" | "staging" | "prod";
const baseUrls: Record<Env, string> = {
  dev: "https://dev.example.com",
  staging: "https://staging.example.com",
  prod: "https://example.com",
};   // ❌ compile error if you forget one
```

---

## 8. Mapped and conditional types

```typescript
// mapped type — transform every property
type Nullable<T> = { [K in keyof T]: T[K] | null };
type Stringify<T> = { [K in keyof T]: string };

// with modifiers
type MyPartial<T> = { [K in keyof T]?: T[K] };
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };
type Mutable<T> = { -readonly [K in keyof T]: T[K] };   // removes readonly

// conditional type
type IsString<T> = T extends string ? true : false;
type A = IsString<"hi">;    // true
type B = IsString<42>;      // false

// infer
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type C = UnwrapPromise<Promise<number>>;   // number

// template literal types — very useful for test selectors
type TestId = `data-test-${string}`;
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type Route = `/${string}`;
type Endpoint = `${HttpMethod} ${Route}`;
const e: Endpoint = "POST /api/users";   // OK
```

---

## 9. Async, promises, error handling

```typescript
// promise typing
const p: Promise<string> = Promise.resolve("done");

async function fetchUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()) as User;
}

// parallel — all must succeed
const [u1, u2] = await Promise.all([fetchUser(1), fetchUser(2)]);

// parallel — collect successes and failures
const results = await Promise.allSettled([fetchUser(1), fetchUser(999)]);
for (const r of results) {
  if (r.status === "fulfilled") console.log(r.value.name);
  else console.error(r.reason);
}

// first to settle
const fastest = await Promise.race([fetchUser(1), timeout(5000)]);

// typed error handling
class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly url: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

try {
  await fetchUser(1);
} catch (e: unknown) {          // always `unknown`, never `any`
  if (e instanceof ApiError) {
    console.error(`${e.status} on ${e.url}`);
  } else if (e instanceof Error) {
    console.error(e.message);
  } else {
    console.error("Unknown failure", e);
  }
}

// a retry helper you will actually reuse in test code
async function retry<T>(
  fn: () => Promise<T>,
  attempts = 3,
  delayMs = 1000
): Promise<T> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (i < attempts - 1) {
        await new Promise((r) => setTimeout(r, delayMs * 2 ** i));  // backoff
      }
    }
  }
  throw lastError;
}
```

---

## 10. Modules

```typescript
// named exports
export const BASE_URL = "https://api.example.com";
export function login() {}
export interface Credentials { user: string; pass: string; }

// default export
export default class ApiClient {}

// re-export (barrel file — src/pages/index.ts)
export * from "./LoginPage";
export * from "./DashboardPage";
export { default as BasePage } from "./BasePage";

// imports
import ApiClient, { BASE_URL, login } from "./api";
import type { Credentials } from "./api";     // type-only import, erased at runtime
import * as helpers from "./helpers";
```

---

## 11. Modern syntax you'll use daily

```typescript
// optional chaining
const city = user?.address?.city;
const result = callback?.();
const firstItem = arr?.[0];

// nullish coalescing — only falls through on null/undefined, not "" or 0
const port = config.port ?? 3000;
const nameA = "" || "default";    // "default"  ← || catches empty string
const nameB = "" ?? "default";    // ""         ← ?? does not

// logical assignment
config.retries ??= 3;
flags.debug ||= false;
counts.total &&= counts.total + 1;

// destructuring with types and defaults
const { id, name = "Anonymous" }: User = user;
const [first, second, ...rest] = [1, 2, 3, 4, 5];

// nested destructuring in params
function render({ user: { name }, theme = "dark" }: Props) {}

// spread
const merged = { ...defaults, ...overrides };
const combined = [...arr1, ...arr2];

// satisfies — validates without widening the type
const config = {
  url: "https://example.com",
  timeout: 30000,
} satisfies { url: string; timeout: number };
config.url.toUpperCase();   // still knows url is the literal string type

// as const — freezes literal types
const ROLES = ["admin", "user", "guest"] as const;
type Role = typeof ROLES[number];   // "admin" | "user" | "guest"
```

---

## 12. Practice checklist for Week 1–2

Tick each only when you've written it **from scratch, without looking**:

- [ ] Typed a function with optional, default, and rest params
- [ ] Written a discriminated union and narrowed it in a switch with exhaustiveness check
- [ ] Written a custom type guard using `obj is Type`
- [ ] Written a generic function with a `extends keyof` constraint
- [ ] Written a generic class (`Repository<T>`)
- [ ] Used `Partial`, `Pick`, `Omit`, and `Record` in real code
- [ ] Written a mapped type and a conditional type with `infer`
- [ ] Written a typed `retry` wrapper with exponential backoff
- [ ] Built a test-data factory using `Partial<T>` overrides
- [ ] Set up a project with `strict: true` and zero `any`

---

**Next:** `02-oops-realtime.md` — OOP concepts mapped onto real Playwright page objects.
