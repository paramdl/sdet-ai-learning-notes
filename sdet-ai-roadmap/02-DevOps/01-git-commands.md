# Git — Complete Command Reference for SDETs

---

## 1. One-time setup

```bash
git config --global user.name "Alex"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true          # Windows line endings
git config --global core.editor "code --wait"
git config --global pull.rebase true            # rebase instead of merge on pull

# useful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.unstage "reset HEAD --"

# view config
git config --list
git config --global --edit
```

---

## 2. Starting a repository

```bash
git init
git init my-project
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git my-folder
git clone --depth 1 https://github.com/user/repo.git    # shallow, fast
git clone -b develop https://github.com/user/repo.git   # specific branch
```

---

## 3. Daily workflow

```bash
git status
git status -s                        # short format

git add file.ts
git add .                            # everything in current dir down
git add -A                           # everything including deletions
git add -p                           # interactive — stage hunk by hunk

git commit -m "feat: add login page object"
git commit -am "fix: flaky checkout test"      # add tracked + commit
git commit --amend                             # edit the last commit
git commit --amend --no-edit                   # add staged changes to last commit

git push
git push origin main
git push -u origin feature/new-tests           # set upstream on first push
git push --force-with-lease                    # safer than --force

git pull
git pull --rebase
git fetch                                      # download without merging
git fetch --all --prune                        # also delete stale remote refs
```

### Commit message convention

```
feat:     new feature or new test coverage
fix:      bug fix, or fixing a broken test
refactor: restructure without behaviour change
test:     adding or updating tests
chore:    tooling, deps, config
docs:     documentation
ci:       pipeline changes
perf:     performance improvement

feat(checkout): add UPI payment page object
fix(login): handle slow redirect causing flake
test(api): add negative cases for /users endpoint
```

---

## 4. Branching

```bash
git branch                           # list local
git branch -a                        # all including remote
git branch -r                        # remote only
git branch -vv                       # with tracking info and last commit

git branch feature/llm-eval
git checkout feature/llm-eval
git checkout -b feature/llm-eval     # create + switch

# modern syntax (git 2.23+)
git switch main
git switch -c feature/new            # create + switch
git restore file.ts                  # discard working changes
git restore --staged file.ts         # unstage

git branch -d feature/done           # delete (safe — refuses if unmerged)
git branch -D feature/abandoned      # force delete
git push origin --delete feature/old # delete remote branch

git branch -m old-name new-name      # rename
```

---

## 5. Merging and rebasing

```bash
git merge feature/login
git merge --no-ff feature/login      # always create a merge commit
git merge --squash feature/login     # combine into one staged change
git merge --abort                    # bail out of a conflicted merge

git rebase main                      # replay my commits on top of main
git rebase -i HEAD~5                 # interactive — squash, reword, drop
git rebase --continue
git rebase --skip
git rebase --abort
```

### Merge vs rebase — the interview answer

**Merge** preserves true history and creates a merge commit. Safe for shared branches.
**Rebase** rewrites your commits onto a new base, producing linear history. Never rebase a branch others have pulled.

**Rule:** rebase your local feature branch onto main before opening a PR; merge the PR into main.

### Resolving conflicts

```bash
git status                           # lists conflicted files
# edit files, remove <<<<<<< ======= >>>>>>> markers
git add resolved-file.ts
git rebase --continue                # or: git commit (for merge)

git checkout --ours file.ts          # take our version
git checkout --theirs file.ts        # take their version
git diff --name-only --diff-filter=U # list unresolved files
git mergetool
```

---

## 6. Inspecting history

```bash
git log
git log --oneline
git log --oneline --graph --decorate --all
git log -5                           # last 5
git log --author="SDET notes"
git log --since="2 weeks ago"
git log --until="2026-09-01"
git log --grep="flaky"               # search commit messages
git log -S "getByRole"               # search for code that added/removed a string
git log -p file.ts                   # full diff per commit for a file
git log --follow file.ts             # follow through renames
git log --stat                       # files changed per commit
git log main..feature                # commits in feature not in main

git show HEAD
git show abc123
git show HEAD~3:path/to/file.ts      # file contents at that commit

git diff                             # working dir vs staged
git diff --staged                    # staged vs last commit
git diff HEAD                        # working dir vs last commit
git diff main feature                # between branches
git diff --name-only main feature
git diff --stat

git blame file.ts
git blame -L 10,20 file.ts

git reflog                           # every HEAD move — your safety net
```

---

## 7. Undoing things

```bash
# discard working directory changes
git restore file.ts
git checkout -- file.ts              # old syntax
git restore .

# unstage
git restore --staged file.ts
git reset HEAD file.ts

# undo commits
git reset --soft HEAD~1              # undo commit, keep changes staged
git reset --mixed HEAD~1             # undo commit, keep changes unstaged (default)
git reset --hard HEAD~1              # undo commit, DESTROY changes

git revert abc123                    # new commit that undoes abc123 — safe for shared branches
git revert HEAD
git revert --no-commit abc123

# recover a deleted branch or lost commit
git reflog
git checkout -b recovered abc123
```

> **`reset` vs `revert`:** `reset` rewrites history — only safe on commits you haven't pushed. `revert` adds a new commit that undoes an old one — safe on shared branches. On a shared branch, always revert.

---

## 8. Stashing

```bash
git stash
git stash save "wip: refactoring page objects"
git stash -u                         # include untracked files
git stash list
git stash show stash@{0}
git stash show -p stash@{0}          # with diff
git stash apply                      # apply, keep in stash
git stash pop                        # apply and remove
git stash apply stash@{2}
git stash drop stash@{0}
git stash clear
git stash branch new-branch          # create a branch from a stash
```

---

## 9. Remotes

```bash
git remote -v
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git
git remote remove origin
git remote rename origin old-origin
git remote set-url origin git@github.com:user/repo.git

git fetch upstream
git merge upstream/main
```

---

## 10. Tags

```bash
git tag
git tag v1.0.0
git tag -a v1.0.0 -m "First stable release"
git tag -a v1.0.0 abc123             # tag an old commit
git show v1.0.0
git push origin v1.0.0
git push origin --tags
git tag -d v1.0.0
git push origin --delete v1.0.0
git checkout v1.0.0
```

---

## 11. Cherry-pick, bisect, worktree

```bash
# take one commit from another branch
git cherry-pick abc123
git cherry-pick abc123..def456
git cherry-pick --abort

# find which commit introduced a bug — binary search
git bisect start
git bisect bad                       # current is broken
git bisect good v1.0.0               # this was fine
# git checks out a midpoint; test it, then:
git bisect good      # or: git bisect bad
# repeat until git names the culprit
git bisect reset

# automate it — brilliant for finding which commit made a test flaky
git bisect run npx playwright test tests/checkout.spec.ts

# multiple branches checked out at once
git worktree add ../repo-hotfix hotfix/urgent
git worktree list
git worktree remove ../repo-hotfix
```

---

## 12. Cleaning

```bash
git clean -n                         # dry run — ALWAYS do this first
git clean -f                         # delete untracked files
git clean -fd                        # + untracked directories
git clean -fdx                       # + ignored files (nukes node_modules)

git gc                               # garbage collect
git prune
```

---

## 13. `.gitignore` for a test repo

```gitignore
node_modules/
dist/
build/

# Playwright
test-results/
playwright-report/
blob-report/
playwright/.cache/
.last-run.json

# secrets and auth state — NEVER commit these
.env
.env.*
!.env.example
auth/*.json
*.pem
*.key

# Python (LLM work)
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.ipynb_checkpoints/

# OS / editor
.DS_Store
Thumbs.db
.vscode/
.idea/

# logs
*.log
npm-debug.log*
```

```bash
# stop tracking a file already committed
git rm --cached .env
git rm -r --cached node_modules

# check why a file is ignored
git check-ignore -v path/to/file
```

---

## 14. The workflow you'll actually use daily

```bash
# start work
git switch main
git pull --rebase
git switch -c feature/llm-eval-harness

# ... work ...
git add -p
git commit -m "feat(eval): add golden dataset loader"

# keep up to date with main
git fetch origin
git rebase origin/main

# push and open a PR
git push -u origin feature/llm-eval-harness
gh pr create --title "Add LLM eval harness" --body "..."

# after merge
git switch main
git pull
git branch -d feature/llm-eval-harness
git fetch --prune
```

---

## 15. GitHub CLI

```bash
gh auth login
gh repo create my-repo --public --source=. --push
gh repo clone user/repo

gh pr create --title "..." --body "..."
gh pr create --fill                  # use commit messages
gh pr list
gh pr view 42
gh pr view 42 --web
gh pr checkout 42
gh pr merge 42 --squash --delete-branch
gh pr diff 42

gh issue create --title "..." --body "..."
gh issue list --assignee @me

gh run list                          # CI runs
gh run view 12345 --log
gh run watch
gh run rerun 12345 --failed
```

---

## 16. Interview questions

**Q. `git fetch` vs `git pull`?**
`fetch` downloads remote changes without touching your working branch. `pull` is `fetch` + `merge` (or `rebase`). I use `fetch` when I want to inspect what changed before integrating it.

**Q. `git merge` vs `git rebase`?**
Merge preserves actual history and adds a merge commit. Rebase replays your commits on a new base, giving linear history but rewriting commit hashes. Rebase local feature branches; never rebase anything others have pulled.

**Q. `git reset` vs `git revert`?**
`reset` moves the branch pointer and rewrites history — only for unpushed commits. `revert` creates a new commit undoing an old one — safe on shared branches. On main, always revert.

**Q. Difference between `--soft`, `--mixed`, `--hard`?**
`--soft` keeps changes staged. `--mixed` (default) keeps them in the working directory, unstaged. `--hard` discards them entirely. Only `--hard` loses work — and even then `reflog` can often recover the commit.

**Q. What is `git cherry-pick` for?**
Applying a single commit from one branch to another. Typical use is a hotfix that must go to both a release branch and main without merging everything else.

**Q. How do you find which commit broke a test?**
`git bisect`. Mark a known-good and known-bad commit, and git binary-searches. With `git bisect run <command>` it's fully automated — I've used it to find which commit made a test flaky by running that spec repeatedly at each step.

**Q. How do you undo a pushed commit?**
`git revert` on a shared branch. `reset --hard` plus `push --force-with-lease` only on a branch you own and nobody else has pulled. `--force-with-lease` rather than `--force` so you don't clobber someone else's push.

**Q. What is `git reflog`?**
A log of every position HEAD has occupied, including ones no longer reachable from any branch. It's how you recover from a bad reset or a deleted branch — the commits survive until garbage collection.

**Q. What goes in `.gitignore` for a test automation repo?**
`node_modules`, build output, `test-results` and `playwright-report`, and critically `.env` files and saved `storageState` JSON — those hold live credentials and sessions. I commit a `.env.example` with the keys and no values.

**Q. What is a merge conflict and how do you resolve it?**
Two branches changed the same lines. Git marks the region with `<<<<<<<`/`=======`/`>>>>>>>`. You pick or combine, delete the markers, `git add`, then continue the merge or rebase. The real prevention is small, frequent merges from main rather than long-lived branches.

**Q. Explain your branching strategy.**
Trunk-based with short-lived feature branches: branch from main, keep it under a few days, rebase before the PR, squash-merge back. Long-lived develop/release branches create merge pain that outweighs their benefit for most teams. Tags mark releases.

---

## Practice checklist

- [ ] Created a repo, committed, pushed, opened a PR, merged it
- [ ] Deliberately created a merge conflict and resolved it
- [ ] Used interactive rebase to squash three commits into one
- [ ] Recovered a "lost" commit using reflog
- [ ] Used `git bisect run` to find a breaking commit automatically
- [ ] Used `git add -p` to stage part of a file
- [ ] Set up `.gitignore` properly and un-tracked an accidentally committed `.env`
- [ ] Used `gh` CLI end to end: create repo → PR → check CI → merge

---

**Next:** `02-docker-commands.md`
