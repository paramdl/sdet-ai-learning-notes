# Git — Complete Notes

## Commands, why & when, common problems, and interview questions

---

# 1. The mental model — read this first

Almost every Git confusion comes from not knowing which of four places your work is in.

| Area | What it is | How things get here |
|---|---|---|
| Working Directory | The files you actually edit on disk | You edit them |
| Staging Area (Index) | A draft of your next commit | `git add` |
| Local Repository | Your committed history, stored in `.git/` | `git commit` |
| Remote Repository | The shared copy on GitHub/GitLab | `git push` |

The flow in one line:

```
edit  →  git add  →  git commit  →  git push
(working)  (staging)   (local repo)   (remote)
```

And the reverse:

```
git fetch  →  git merge/rebase  →  your branch
git pull   =  fetch + merge (or rebase)
```

**Why this matters:** when a command "loses" your work, it is almost always sitting in one of these four places. `git status` tells you which. Nearly every "help, I broke Git" moment is solved by first asking *which area is this change in?*

### Three more concepts

**A commit is a snapshot, not a diff.** Git stores the full state of your tree at each commit (deduplicated internally). Diffs are computed on demand. This is why checking out an old commit is fast and safe.

**A branch is just a movable pointer to a commit.** That is all. Creating a branch is instant and costs nothing — it writes a 41-byte file. This is why branching in Git is cheap while it was expensive in older tools like SVN.

**HEAD is a pointer to where you are now.** Usually it points at a branch, which points at a commit. When it points directly at a commit instead, you are in "detached HEAD" state.

---

# 2. One-time setup

## Identity and basics

```bash
git config --global user.name "Alex"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"
```

**Why:** every commit records author name and email permanently. Set this before your first commit or you will have commits attributed to nothing, and rewriting them later is painful.

## Windows-specific

```bash
git config --global core.autocrlf true
git config --global core.longpaths true
```

**Why `core.autocrlf`:** Windows uses CRLF line endings, Linux and Mac use LF. Without this, every file looks entirely modified when a teammate on Mac touches it, and diffs become useless. `true` converts to LF on commit and back to CRLF on checkout.

**Why `core.longpaths`:** Windows has a 260-character path limit. Deep `node_modules` trees exceed it and checkouts fail with cryptic errors.

## Pull behaviour

```bash
git config --global pull.rebase true
```

**Why:** the default `pull` creates a merge commit every time you sync, littering history with "Merge branch 'main' of github.com..." commits that say nothing. Rebasing replays your work on top instead, keeping history linear and readable.

## Aliases that save real time

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm "commit -m"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.unstage "reset HEAD --"
git config --global alias.amend "commit --amend --no-edit"
```

**When to use `git lg`:** any time you are confused about branch state. A visual graph answers "where am I and how did I get here" faster than any other command.

## Viewing and fixing config

```bash
git config --list                    # everything, merged
git config --list --show-origin      # and which file each came from
git config --global --edit           # open the global config file
git config user.email                # check one value
```

**Common issue:** commits showing the wrong author. Cause is usually a repo-local config overriding global. `git config --list --show-origin` shows you exactly which file is winning.

---

# 3. Starting a repository

```bash
git init                                          # new repo here
git init my-project                               # new repo in a new folder
git clone https://github.com/user/repo.git        # copy a remote
git clone https://github.com/user/repo.git my-dir # into a named folder
git clone --depth 1 https://...                   # shallow — latest commit only
git clone -b develop https://...                  # a specific branch
git clone --single-branch -b main https://...     # only one branch's history
```

**When to use `--depth 1`:** CI pipelines and one-off inspections. A repo with ten years of history can be 2 GB; a shallow clone is 20 MB. Do not use it if you need to run `git log`, `git bisect`, or `git blame` — the history is not there.

---

# 4. The daily workflow

## Checking state

```bash
git status
git status -s          # short: XY filename
git status -sb         # short + branch info
```

**Why run this constantly:** it is the single most useful command in Git. It tells you what branch you are on, what is staged, what is modified, what is untracked, and often suggests the exact command you need next.

Reading `git status -s`:

```
 M file.ts     modified, not staged     (space then M)
M  file.ts     modified and staged      (M then space)
MM file.ts     staged, then modified again
A  file.ts     newly added, staged
D  file.ts     deleted
?? file.ts     untracked
UU file.ts     both modified — conflict
```

## Staging

```bash
git add file.ts
git add src/            # a directory
git add .               # everything from here down
git add -A              # everything in the repo, including deletions
git add -u              # only already-tracked files
git add -p              # interactive: choose hunk by hunk
git add "*.ts"          # by pattern
```

**When to use `git add -p`:** when you fixed three unrelated things in one sitting. It walks you through each change and asks whether to stage it, letting you build three clean commits instead of one messy one. This is the habit that most improves the quality of your history — and reviewers notice.

**`git add .` vs `git add -A`:** `.` stages from the current directory down; `-A` stages the whole repo regardless of where you are. In modern Git the difference is small, but `-A` is what you want when you have deleted files.

## Committing

```bash
git commit -m "feat: add login page object"
git commit                       # opens editor for a longer message
git commit -am "fix: flaky test" # add tracked files and commit in one step
git commit --amend               # change the last commit
git commit --amend --no-edit     # add staged changes to last commit, keep message
git commit --allow-empty -m "trigger CI"
```

**When to use `-am`:** small fixes to files Git already tracks. It will **not** pick up new files, which is a frequent surprise — you commit, push, and the new file is missing.

**When to use `--amend`:** you just committed and immediately realised you forgot a file or made a typo in the message. Only safe **before pushing** — see the rewriting-history warning in section 7.

## Commit message convention

```
feat:     a new feature or new test coverage
fix:      a bug fix, or fixing a broken test
refactor: restructuring with no behaviour change
test:     adding or updating tests
chore:    tooling, dependencies, config
docs:     documentation
ci:       pipeline changes
perf:     performance improvement
```

Examples:

```
feat(checkout): add UPI payment page object
fix(login): handle slow redirect causing flake
test(api): add negative cases for /users endpoint
refactor(pages): extract TableComponent from UsersPage
```

**Why bother:** a scannable history means you can find when something changed in seconds. It also enables automated changelogs and semantic versioning. In an interview, being able to explain conventional commits signals you have worked on a team with real standards.

## Pushing and pulling

```bash
git push
git push origin main
git push -u origin feature/new-tests   # first push: set upstream
git push --force-with-lease            # safe force
git push --all
git push --tags

git pull
git pull --rebase
git fetch                              # download, do not merge
git fetch --all --prune                # and delete stale remote-tracking refs
```

**Why `--prune` matters:** when a teammate deletes a remote branch, your local list still shows it forever. `--prune` cleans those up. Without it, `git branch -r` becomes a graveyard.

**Why `--force-with-lease` instead of `--force`:** plain `--force` overwrites the remote unconditionally, destroying any commits a teammate pushed in the meantime. `--force-with-lease` checks that the remote is still where you last saw it and refuses if someone else has pushed. Make this a reflex — it is one of the few Git habits that prevents genuinely unrecoverable damage to other people's work.

---

# 5. Branching

```bash
git branch                    # list local branches
git branch -a                 # all, including remote-tracking
git branch -r                 # remote-tracking only
git branch -vv                # with upstream and last commit
git branch --merged           # already merged into current branch
git branch --no-merged        # not yet merged

git branch feature/llm-eval           # create, stay put
git checkout feature/llm-eval         # switch
git checkout -b feature/llm-eval      # create and switch
git checkout -b feature/x origin/main # branch from a remote branch

git branch -d feature/done            # delete — refuses if unmerged
git branch -D feature/abandoned       # force delete
git push origin --delete feature/old  # delete on the remote
git branch -m old-name new-name       # rename
```

## The modern syntax — prefer these

```bash
git switch main                # switch branches
git switch -c feature/new      # create and switch
git switch -                   # back to previous branch
git switch --detach abc123     # deliberately detach HEAD

git restore file.ts            # discard working changes to a file
git restore .                  # discard all working changes
git restore --staged file.ts   # unstage, keep the edit
git restore --source=HEAD~2 file.ts   # get a file from an older commit
```

**Why these exist:** `git checkout` did too many unrelated things — switching branches, discarding changes, restoring files. That overloading is why people accidentally destroyed work. Git 2.23 split it into `switch` (branches) and `restore` (file contents). Use them; mention in an interview that you know why they were introduced.

## Branch naming

```
feature/add-payment-tests
fix/login-flake
refactor/page-objects
chore/upgrade-playwright
hotfix/prod-500-error
```

**Why:** prefixes make branch lists scannable and let CI rules target categories (for example, run the full suite only on `release/*`).

---

# 6. Merging and rebasing

## Commands

```bash
git merge feature/login
git merge --no-ff feature/login    # always create a merge commit
git merge --squash feature/login   # combine all changes into one staged set
git merge --abort                  # back out of a conflicted merge

git rebase main                    # replay my commits on top of main
git rebase -i HEAD~5               # interactive: squash, reword, reorder, drop
git rebase --continue
git rebase --skip
git rebase --abort
git rebase --onto main develop feature   # advanced: move a branch's base
```

## The difference, precisely

Say you branched from main, then main moved on.

**Merge** creates a new commit with two parents, joining the histories:

```
main:     A---B---C-------M
                   \     /
feature:            D---E
```

**Rebase** rewrites D and E as new commits on top of C:

```
main:     A---B---C
                   \
feature:            D'--E'
```

D and E still exist briefly in the reflog, but D' and E' are **new commits with new hashes**. This is the crucial point.

## When to use which

| Situation | Use | Why |
|---|---|---|
| Updating your local feature branch from main | Rebase | Keeps history linear, avoids merge-commit noise |
| Bringing a finished feature into main | Merge | Preserves the true record of when it landed |
| A branch nobody else has pulled | Rebase freely | No one else's history depends on it |
| A branch teammates have pulled | **Never rebase** | Rewriting shared history forces everyone into painful recovery |
| Many small messy WIP commits | Interactive rebase or squash merge | Reviewers want one coherent change |
| You want an exact audit trail | Merge, `--no-ff` | Shows precisely what happened and when |

**The rule in one sentence:** rebase your own local branch to keep it current, merge to integrate finished work, and never rebase anything that has left your machine.

## Interactive rebase

```bash
git rebase -i HEAD~4
```

You get an editor:

```
pick a1b2c3 add login page object
pick d4e5f6 fix typo
pick g7h8i9 fix another typo
pick j0k1l2 add login tests
```

Change the verbs:

```
pick   a1b2c3 add login page object
squash d4e5f6 fix typo
squash g7h8i9 fix another typo
pick   j0k1l2 add login tests
```

Result: two clean commits instead of four.

Available verbs:

| Verb | Effect |
|---|---|
| `pick` | keep the commit as is |
| `reword` | keep changes, edit the message |
| `edit` | stop here so you can amend the content |
| `squash` | merge into previous, combine messages |
| `fixup` | merge into previous, discard this message |
| `drop` | delete the commit entirely |
| `reorder` | just move the lines |

**When to use:** immediately before opening a pull request. Turn your eleven "wip", "fix", "actually fix" commits into two or three that tell a story. Reviewers read commits; messy history genuinely slows review down.

## Squash merge

```bash
git merge --squash feature/login
git commit -m "feat(login): add login flow with page objects and tests"
```

**When:** the feature branch's individual commits have no lasting value. Most teams configure GitHub to squash-merge pull requests for exactly this reason — one PR becomes one commit on main.

**Trade-off:** you lose the granular history. If a feature took three weeks and has meaningful intermediate steps, a normal merge preserves more useful information.

---

# 7. Undoing things — the decision tree

This is where people panic. Work through it by asking two questions: **where is the change**, and **has it been pushed?**

## Case 1 — I edited a file and want the original back

```bash
git restore file.ts        # modern
git checkout -- file.ts    # older syntax
git restore .              # all files
```

**Destructive.** The edit is not in Git anywhere, so it is gone. If you are unsure, `git stash` first — that keeps it recoverable.

## Case 2 — I staged something I did not mean to

```bash
git restore --staged file.ts    # unstage, keep the edit
git reset HEAD file.ts          # same thing, older syntax
git reset                       # unstage everything
```

**Safe.** Your edits survive; only the staging is undone.

## Case 3 — I committed but have not pushed

```bash
git commit --amend                 # fix the message or add staged files
git reset --soft HEAD~1            # undo commit, changes stay staged
git reset --mixed HEAD~1           # undo commit, changes unstaged (default)
git reset --hard HEAD~1            # undo commit and DESTROY the changes
git reset --hard HEAD~3            # undo the last three commits
```

The three flags, compared:

| Flag | Branch pointer | Staging area | Working directory |
|---|---|---|---|
| `--soft` | moves back | **kept** | kept |
| `--mixed` | moves back | cleared | **kept** |
| `--hard` | moves back | cleared | **cleared** |

**When to use `--soft`:** you want to recommit the same work differently — split it, or write a better message.

**When to use `--hard`:** you are certain the work is worthless. Even then, the commit survives in the reflog for about 90 days, so it is recoverable — see section 8.

## Case 4 — I pushed, and others may have pulled

```bash
git revert abc123              # create a NEW commit that undoes abc123
git revert HEAD                # undo the most recent commit
git revert HEAD~2..HEAD        # undo a range
git revert -m 1 <merge-sha>    # undo a merge commit, keeping parent 1
git revert --no-commit abc123  # stage the undo without committing
```

**Why revert and not reset:** `reset` rewrites history. If the commit is already on the remote and a teammate has pulled it, rewriting means their history and yours have diverged, and every one of them has to recover manually. `revert` adds a new commit that cancels the old one — everyone just pulls normally. It is the only safe choice on a shared branch.

**Trade-off:** the bad commit stays visible in history. That is usually correct — an audit trail should show that a mistake was made and fixed.

## Case 5 — I need to undo a merge

```bash
git revert -m 1 <merge-commit-sha>
```

**Why `-m 1`:** a merge commit has two parents. `-m 1` means "keep the first parent's line of history" — normally the branch you merged into. Without `-m`, Git refuses because it cannot guess which side you want.

## The hard rule on rewriting history

Rewriting commits that exist on a remote and have been pulled by others is the one genuinely damaging thing you can do in Git. `commit --amend`, `rebase`, and `reset --hard` all rewrite. Before using any of them, ask: **has anyone else seen these commits?** If yes, use `revert` instead.

---

# 8. Recovering from disaster — the reflog

```bash
git reflog                    # every position HEAD has held
git reflog show main          # for a specific branch
git reflog --date=iso
```

Output:

```
a1b2c3d HEAD@{0}: reset: moving to HEAD~3
e4f5g6h HEAD@{1}: commit: add payment tests
i7j8k9l HEAD@{2}: commit: add checkout page object
```

**Recovery:**

```bash
git reset --hard HEAD@{1}         # go back to before the bad reset
git checkout -b recovered e4f5g6h # or make a branch from the lost commit
git cherry-pick e4f5g6h           # or grab just that one commit
```

**Why this works:** Git does not delete commits when you move a branch pointer. They become "unreachable" but survive in the object database until garbage collection, typically 90 days later. The reflog is your local log of every pointer move, which is how you find them again.

**When you need it:** after a bad `reset --hard`, a botched rebase, or deleting a branch that was not merged. It has saved more work than any other Git feature.

```bash
git fsck --lost-found         # find dangling commits not even in the reflog
```

---

# 9. Stashing

```bash
git stash                            # shelve tracked modifications
git stash push -m "wip: refactoring" # with a message
git stash -u                         # include untracked files
git stash -a                         # include ignored files too
git stash push file.ts               # stash one specific file

git stash list
git stash show stash@{0}
git stash show -p stash@{0}          # with the full diff

git stash apply                      # restore, keep it in the stash list
git stash pop                        # restore and remove from the list
git stash apply stash@{2}
git stash drop stash@{0}
git stash clear                      # delete all stashes
git stash branch new-branch          # create a branch from a stash
```

**When to use:** you are mid-change and need to switch branches urgently, or pull requires a clean tree.

**Common issue — forgotten stashes.** Stashes are invisible in normal workflow and accumulate silently. People lose days of work this way. Two habits fix it: always use `-m` with a description, and run `git stash list` weekly.

**`apply` vs `pop`:** use `apply` when you might need the stash again (for example, applying the same change to two branches). Use `pop` for the normal case. If `pop` hits a conflict, the stash is **not** dropped, so nothing is lost.

---

# 10. Inspecting history

## Log

```bash
git log
git log --oneline
git log --oneline --graph --decorate --all     # the one to memorise
git log -5
git log --stat                                 # files changed per commit
git log -p                                      # full diffs
git log --author="SDET notes"
git log --since="2 weeks ago" --until="yesterday"
git log --grep="flaky"                         # search commit messages
git log -S "getByRole"                         # search for code that changed
git log -G "getBy.*Role"                       # same, regex
git log --follow file.ts                       # history through renames
git log main..feature                          # in feature, not in main
git log feature..main                          # in main, not in feature
git log --no-merges
git log --merges
git log --pretty=format:"%h %an %ar %s"
```

**When to use `-S`:** you need to know when a specific string entered or left the codebase — "when did this selector change?" This is called a pickaxe search and it is far faster than reading diffs.

**When to use `main..feature`:** before opening a PR, to review exactly what you are proposing.

## Show, diff, blame

```bash
git show HEAD
git show abc123
git show abc123 --stat
git show HEAD~3:src/pages/LoginPage.ts    # a file as it was then

git diff                                   # working dir vs staging
git diff --staged                          # staging vs last commit
git diff HEAD                              # working dir vs last commit
git diff main feature                      # between branches
git diff main...feature                    # since they diverged
git diff --name-only main feature
git diff --stat
git diff abc123 def456 -- file.ts

git blame file.ts
git blame -L 20,40 file.ts                 # just those lines
git blame -w file.ts                       # ignore whitespace-only changes
git blame --ignore-rev <reformat-sha>      # skip a mass-reformat commit
```

**Why `blame --ignore-rev` matters:** a single "run prettier on everything" commit makes `blame` useless for the whole repo, attributing every line to whoever ran the formatter. This flag skips it. Teams often keep a `.git-blame-ignore-revs` file listing such commits.

**When to use blame carefully:** to understand *why* a line exists, not to find someone to blame. Use it to find the commit, then read that commit's message and PR for the reasoning.

---

# 11. Remotes

```bash
git remote -v
git remote show origin
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git
git remote remove origin
git remote rename origin old-origin
git remote set-url origin git@github.com:user/repo.git
git remote prune origin --dry-run
```

**The fork workflow:** `origin` is your fork, `upstream` is the original.

```bash
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

## HTTPS vs SSH

```bash
# HTTPS — needs a Personal Access Token as the password
https://github.com/user/repo.git

# SSH — needs a key pair
git@github.com:user/repo.git

ssh-keygen -t ed25519 -C "you@example.com"
cat ~/.ssh/id_ed25519.pub        # add this to GitHub → Settings → SSH keys
ssh -T git@github.com            # test it
```

**Why switch to SSH:** GitHub removed password authentication in 2021. With HTTPS you must generate a token and paste it as your password; with SSH the key handles it silently. For daily work SSH is less friction.

---

# 12. Tags

```bash
git tag                              # list
git tag -l "v1.*"
git tag v1.0.0                       # lightweight
git tag -a v1.0.0 -m "First stable"  # annotated — preferred
git tag -a v1.0.0 abc123             # tag an older commit
git show v1.0.0
git push origin v1.0.0
git push origin --tags
git tag -d v1.0.0                    # delete locally
git push origin --delete v1.0.0      # delete on remote
git checkout v1.0.0                  # detached HEAD at that tag
git describe --tags                  # nearest tag plus distance
```

**Lightweight vs annotated:** a lightweight tag is just a pointer. An annotated tag is a real object with a tagger, date, message, and optional signature. **Always use annotated (`-a`) for releases** — you want to know who cut it and when.

**Common issue:** tags are not pushed by `git push`. You must push them explicitly. People wonder why their release tag is missing from GitHub for exactly this reason.

---

# 13. Cherry-pick, bisect, worktree

## Cherry-pick

```bash
git cherry-pick abc123
git cherry-pick abc123 def456
git cherry-pick abc123..def456      # a range, exclusive of abc123
git cherry-pick abc123^..def456     # inclusive
git cherry-pick -x abc123           # note the original sha in the message
git cherry-pick --no-commit abc123
git cherry-pick --abort
git cherry-pick --continue
```

**When:** a hotfix must go to both `main` and a release branch without dragging along everything else on the branch.

**Why `-x`:** it records "cherry picked from commit abc123" in the message, so six months later you can see the relationship. Use it whenever you cherry-pick across long-lived branches.

**Common issue — duplicate commits.** Cherry-picking creates a *new* commit with the same changes but a different hash. If the branch is later merged normally, Git usually handles it, but you can get confusing conflicts. Prefer cherry-picking only in the hotfix direction.

## Bisect — find the commit that broke something

```bash
git bisect start
git bisect bad                 # current state is broken
git bisect good v1.0.0         # this version was fine
# Git checks out a midpoint. Test it, then:
git bisect good                # or: git bisect bad
# repeat until Git names the culprit
git bisect reset               # return to where you started
```

Automated — and this is the version worth knowing:

```bash
git bisect start HEAD v1.0.0
git bisect run npx playwright test tests/checkout.spec.ts
```

```bash
# find which commit made a test flaky
git bisect run bash -c "npx playwright test tests/login.spec.ts --repeat-each=20"
```

**Why this is powerful:** binary search over history. Finding a regression among 1,000 commits takes about ten steps instead of a thousand. With `bisect run` it is fully hands-off — you go and do something else while Git finds it.

**As a testing story:** being able to say "I used `git bisect run` with a repeat-each loop to find the commit that introduced a flaky test" is a strong, concrete, credible answer to "how do you deal with flakiness."

## Worktree — multiple branches checked out at once

```bash
git worktree add ../repo-hotfix hotfix/urgent
git worktree add -b new-branch ../repo-new
git worktree list
git worktree remove ../repo-hotfix
git worktree prune
```

**When:** you are mid-refactor with a dirty tree and a production bug lands. Instead of stashing, get a second working directory sharing the same `.git`. Both stay independent.

**Why better than a second clone:** it shares the object database, so it is instant and uses almost no extra disk. Very useful when a build takes ten minutes and you do not want to lose the warm state of your main worktree.

---

# 14. .gitignore

```gitignore
# dependencies
node_modules/
.venv/
__pycache__/

# build output
dist/
build/
*.tsbuildinfo

# Playwright
test-results/
playwright-report/
blob-report/
playwright/.cache/
.last-run.json

# secrets — NEVER commit these
.env
.env.*
!.env.example
auth/*.json
*.pem
*.key
credentials.json

# OS and editor
.DS_Store
Thumbs.db
.idea/
.vscode/*
!.vscode/settings.json

# logs
*.log
npm-debug.log*
```

## Patterns

```
file.txt        that name anywhere
/file.txt       only at the repo root
dir/            a directory and everything in it
*.log           by extension
!important.log  negate — track this despite a broader rule
**/temp         temp at any depth
docs/**/*.pdf   PDFs at any depth under docs
```

## Commands

```bash
git check-ignore -v path/to/file     # why is this ignored?
git rm --cached .env                 # stop tracking, keep the file on disk
git rm -r --cached node_modules
git rm --cached -r . && git add .    # re-apply gitignore to everything
git status --ignored
```

**The single most important issue in this whole document:** `.gitignore` only affects **untracked** files. If you committed `.env` before adding it to `.gitignore`, it stays tracked and keeps getting committed. You must `git rm --cached .env` to stop it.

**And worse:** that file is now in your history forever. Adding it to `.gitignore` afterwards does not remove it from past commits. Anyone who clones the repo gets the secret. See section 15 for the fix — and treat the credential as compromised regardless.

---

# 15. Common problems and how to fix them

## "Your branch and 'origin/main' have diverged"

```bash
git log --oneline --graph --all     # see the shape of the problem
git pull --rebase                  # usually the right answer
```

**Cause:** you have local commits and the remote has different commits. Someone force-pushed, or you amended something already pushed.

## "Updates were rejected because the remote contains work you do not have"

```bash
git pull --rebase
git push
```

**Never** reach for `git push --force` here. That is how you delete a colleague's work.

## Merge conflict

```bash
git status                              # lists the conflicted files
```

You will see markers in the file:

```
<<<<<<< HEAD
const timeout = 30000;
=======
const timeout = 60000;
>>>>>>> feature/slow-tests
```

Fix it by hand, delete all three marker lines, then:

```bash
git add file.ts
git rebase --continue      # if rebasing
git commit                 # if merging
```

Helpers:

```bash
git diff --name-only --diff-filter=U    # list unresolved files
git checkout --ours file.ts             # take the current branch's version
git checkout --theirs file.ts           # take the incoming version
git merge --abort                       # give up on the merge
git rebase --abort
git mergetool
```

**Confusing detail:** during a **rebase**, "ours" and "theirs" are swapped relative to a merge, because rebase replays your commits onto the other branch. When in doubt, look at the actual content rather than trusting the label.

**Prevention:** merge from main into your branch often. A branch that lives for three weeks without syncing will produce a brutal conflict; one that syncs daily rarely conflicts at all.

## "Detached HEAD"

```bash
git switch -                       # back to where you were
git switch -c new-branch           # keep the work on a new branch
```

**Cause:** you checked out a commit or tag directly instead of a branch. HEAD points at a commit rather than a branch name.

**The danger:** commits you make here belong to no branch. If you switch away, they become unreachable — recoverable via reflog, but easy to lose. If you have made commits in detached HEAD, create a branch before switching away.

## I committed to the wrong branch

Not yet pushed:

```bash
git log --oneline -1               # note the sha
git reset --hard HEAD~1            # remove it from the wrong branch
git switch correct-branch
git cherry-pick <sha>
```

Or move several commits:

```bash
git switch -c correct-branch       # take the commits with you
git switch wrong-branch
git reset --hard origin/wrong-branch
```

## I committed a huge file and now push fails

GitHub rejects files over 100 MB.

```bash
# if it is the most recent commit and not yet pushed
git rm --cached huge-file.zip
echo "huge-file.zip" >> .gitignore
git commit --amend

# if it is buried deeper in history
pip install git-filter-repo
git filter-repo --path huge-file.zip --invert-paths
git push --force-with-lease
```

**Warning:** `filter-repo` rewrites every commit after the one touched, changing all their hashes. Everyone must re-clone. Coordinate before doing it.

## I committed a secret

```bash
# 1. Rotate the credential FIRST. Assume it is compromised.
# 2. Then remove it from history:
pip install git-filter-repo
git filter-repo --path .env --invert-paths
git push --force-with-lease
```

**The order matters and this is the point most people get wrong.** Rewriting history does not un-leak the secret — it may be in someone's clone, in a CI log, in a fork, or already indexed by a scraper. Rotating the credential is the actual fix; cleaning history is housekeeping.

## Line endings: every file shows as modified

```bash
git config --global core.autocrlf true
git rm --cached -r .
git reset --hard
```

Better, commit a `.gitattributes` so the setting travels with the repo:

```gitattributes
* text=auto
*.sh text eol=lf
*.bat text eol=crlf
*.png binary
```

**Why `.gitattributes` beats config:** it lives in the repo, so every contributor gets the same behaviour without configuring anything. This is the correct fix for a mixed Windows/Mac team.

## "fatal: refusing to merge unrelated histories"

```bash
git pull origin main --allow-unrelated-histories
```

**Cause:** you created a repo locally with commits, then added a remote that already had its own initial commit. Two independent histories with no common ancestor.

## Wrong author on commits

```bash
git config user.email                        # check the repo-local value
git config user.email "correct@example.com"

git commit --amend --reset-author            # fix just the last one

# fix many (rewrites history — coordinate first)
git rebase -i HEAD~10 --exec "git commit --amend --no-edit --reset-author"
```

## Large repo is slow

```bash
git gc                        # garbage collect and repack
git gc --aggressive --prune=now
git count-objects -vH         # see what is taking space
git maintenance start         # schedule automatic upkeep
```

## Accidentally deleted a branch

```bash
git reflog                            # find its last commit
git switch -c recovered-branch abc123
```

Only works while the commits survive garbage collection — usually 90 days. Act promptly.

## Permission denied (publickey)

```bash
ssh -T git@github.com                 # test the connection
ssh-add -l                            # is a key loaded?
ssh-add ~/.ssh/id_ed25519             # load it
eval "$(ssh-agent -s)"                # start the agent if it is not running
```

## Cleaning untracked files

```bash
git clean -n         # DRY RUN — always do this first
git clean -f         # delete untracked files
git clean -fd        # and untracked directories
git clean -fdx       # and ignored files — this deletes node_modules
```

**`git clean -fdx` is irreversible.** Nothing it deletes is in Git. Run `-n` first, every single time.

---

# 16. Workflow recipes

## Daily feature work

```bash
git switch main
git pull --rebase
git switch -c feature/llm-eval-harness

# ... work ...
git add -p
git commit -m "feat(eval): add golden dataset loader"

# keep current with main
git fetch origin
git rebase origin/main

# tidy up before review
git rebase -i origin/main

git push -u origin feature/llm-eval-harness
gh pr create --fill

# after it merges
git switch main
git pull
git branch -d feature/llm-eval-harness
git fetch --prune
```

## Emergency hotfix while mid-work

```bash
git stash push -m "wip: refactoring page objects"
git switch main
git pull
git switch -c hotfix/prod-500

# ... fix, commit, push, PR, merge ...

git switch feature/my-work
git stash pop
```

Or with worktree, avoiding the stash entirely:

```bash
git worktree add ../repo-hotfix -b hotfix/prod-500 main
cd ../repo-hotfix
# ... fix and push ...
cd -
git worktree remove ../repo-hotfix
```

## Reviewing someone's PR locally

```bash
gh pr checkout 42
npm ci
npx playwright test
git switch -                # back to your own work
```

## Finding a regression

```bash
git bisect start HEAD v1.4.0
git bisect run npx playwright test tests/checkout.spec.ts
git bisect reset
```

---

# 17. GitHub CLI

```bash
gh auth login
gh auth status

gh repo create my-repo --public --source=. --push
gh repo clone user/repo
gh repo view --web

gh pr create --title "Add LLM eval harness" --body "..."
gh pr create --fill              # use commit messages
gh pr create --draft
gh pr list
gh pr list --author @me
gh pr view 42
gh pr view 42 --web
gh pr checkout 42
gh pr diff 42
gh pr review 42 --approve
gh pr review 42 --request-changes --body "..."
gh pr merge 42 --squash --delete-branch
gh pr status

gh issue create --title "..." --body "..."
gh issue list --assignee @me
gh issue close 10

gh run list                      # CI runs
gh run view 12345 --log
gh run view 12345 --log-failed   # only the failing steps
gh run watch
gh run rerun 12345 --failed
gh workflow list
gh workflow run tests.yml -f suite=smoke
```

**Why `gh run view --log-failed`:** on a failing CI run it jumps straight to the failing step's output instead of making you scroll a 4,000-line log in a browser.

---

# 18. Interview questions

## Fundamentals

**Q1. What is Git and how does it differ from SVN?**
Git is a distributed version control system — every clone is a complete repository with full history, so commits, branches, diffs, and log searches all work offline. SVN is centralised: there is one authoritative server, history lives only there, and most operations need a network round trip. The practical consequences are that Git branching is nearly free while SVN branching is expensive, and that Git has no single point of failure.

**Q2. What are the four areas of Git?**
Working directory, staging area (index), local repository, remote repository. `git add` moves changes from working directory to staging; `git commit` from staging to local repo; `git push` from local to remote. Knowing which area a change sits in is how you decide which undo command to use.

**Q3. What is the staging area for? Why not commit directly?**
It lets you compose a commit deliberately rather than dumping everything you touched. If I fixed a bug and also renamed a variable elsewhere, `git add -p` lets me stage and commit them separately so each commit is one logical change. That matters because reviewers read commits, and because `git revert` and `git bisect` only work cleanly when commits are atomic.

**Q4. Is a commit a snapshot or a diff?**
A snapshot of the whole tree, with content-addressed storage deduplicating unchanged files. Diffs are computed when you ask for them. That is why checking out any commit is fast regardless of its age.

**Q5. What is HEAD?**
A pointer to your current position — normally to a branch, which points to a commit. `HEAD~1` is its parent, `HEAD~3` three back. When HEAD points straight at a commit instead of a branch you are in detached HEAD state, and any commits you make there belong to no branch.

**Q6. What is a branch, technically?**
A movable pointer to a commit — literally a small file containing a SHA. That is why creating one is instant and costs nothing, which is what makes short-lived feature branches practical.

## Everyday commands

**Q7. `git fetch` vs `git pull`?**
`fetch` downloads remote changes and updates remote-tracking branches without touching your working branch. `pull` is `fetch` plus `merge` or `rebase`. I use `fetch` plus `log origin/main..main` when I want to see what is coming before integrating it — particularly on a long-lived branch where a surprise merge would be disruptive.

**Q8. `git merge` vs `git rebase`?**
Merge creates a commit with two parents, preserving the real shape of history. Rebase replays your commits onto a new base, producing new commits with new hashes and a linear history. I rebase my own feature branch onto main to stay current, and merge the PR into main. I never rebase a branch anyone else has pulled, because rewriting shared history forces every one of them into manual recovery.

**Q9. `git reset` vs `git revert` vs `git checkout`?**
`reset` moves the branch pointer and rewrites history — only safe on unpushed commits. `revert` creates a new commit that undoes an old one — safe on shared branches, which is why it is the only correct choice on main. `checkout` (now `switch` and `restore`) changes what you have checked out or restores file contents without touching history.

**Q10. Explain `--soft`, `--mixed`, `--hard`.**
All three move the branch pointer. `--soft` leaves your changes staged. `--mixed`, the default, leaves them in the working directory unstaged. `--hard` discards them. Only `--hard` loses work, and even then the commit survives in the reflog for around 90 days.

**Q11. What does `git stash` do and when do you use it?**
Shelves uncommitted changes so you have a clean tree. I use it when a production issue needs attention mid-change. `apply` keeps the stash, `pop` removes it. In practice I prefer `git worktree` for anything longer than a few minutes, because stashes are invisible in normal workflow and easy to forget — I have seen people lose days of work to a forgotten stash.

**Q12. What is cherry-pick for, and what is the risk?**
Applying a single commit's changes to another branch — typically a hotfix that must reach both main and a release branch. The risk is duplication: it creates a new commit with the same content and a different hash, so if the branches are later merged you can get confusing conflicts. I use `-x` so the message records the original SHA.

**Q13. `git add .` vs `git add -A` vs `git add -u`?**
`.` stages everything from the current directory down. `-A` stages the whole repo including deletions. `-u` stages only files Git already tracks. The one that catches people is `git commit -am`, which stages tracked files only — new files are silently left out.

## Problem solving

**Q14. How do you find which commit broke something?**
`git bisect`. Mark a known-good and known-bad commit and Git binary-searches, so 1,000 commits take about ten steps. With `git bisect run <command>` it is fully automated. I have used it with `--repeat-each=20` on a Playwright spec to find the commit that introduced a flaky test — which is much more reliable than reading diffs and guessing.

**Q15. You pushed a commit with a bug to main. What do you do?**
`git revert <sha>` and push. That creates a new commit undoing it, so everyone just pulls normally. I would not `reset --hard` and force-push, because teammates who already pulled would have diverged history. If the fix is trivial and urgent I might push a forward fix instead — the deciding factor is which is easier to review under pressure.

**Q16. How do you recover a commit after `git reset --hard`?**
`git reflog` to find the SHA, then `git reset --hard HEAD@{1}` or `git checkout -b recovered <sha>`. Git does not delete commits when a pointer moves — they become unreachable but survive until garbage collection. If the commit is not even in the reflog, `git fsck --lost-found`.

**Q17. How do you handle a merge conflict?**
`git status` to list conflicted files, edit each to the correct result, remove the conflict markers, `git add`, then continue the merge or rebase. During a rebase "ours" and "theirs" are reversed relative to a merge, so I check the actual content rather than trusting the labels. The real answer is prevention: sync from main daily so conflicts stay small.

**Q18. You committed a secret and pushed. What now?**
Rotate the credential first — that is the actual fix. Rewriting history does not un-leak it; it may already be in a clone, a fork, a CI log, or a scraper's index. Then remove it from history with `git filter-repo`, force-push, and tell the team to re-clone. Going forward, add it to `.gitignore`, commit a `.env.example` with keys and no values, and ideally add a pre-commit secret scanner.

**Q19. Why does `.gitignore` not work on a file?**
Because it only applies to untracked files. If the file was committed before being ignored, it stays tracked. `git rm --cached <file>` stops tracking it while keeping it on disk. `git check-ignore -v <file>` tells you which rule matched — or that none did.

**Q20. What is detached HEAD and why does it matter?**
HEAD points directly at a commit rather than a branch, which happens when you check out a commit or tag. Commits made there belong to no branch, so switching away makes them unreachable. `git switch -c <name>` before leaving preserves them.

**Q21. How do you undo a merge commit?**
`git revert -m 1 <merge-sha>`. The `-m 1` says keep the first parent's history — normally the branch you merged into. Git refuses without `-m` because a merge has two parents and it cannot guess which side you want to keep.

**Q22. `--force` vs `--force-with-lease`?**
`--force` overwrites the remote unconditionally, destroying any commits pushed since you last fetched. `--force-with-lease` verifies the remote is still where you last saw it and refuses otherwise. I use `--force-with-lease` as a reflex — it is one of the few habits that prevents genuinely unrecoverable loss of someone else's work.

## Workflow and team practice

**Q23. Describe your branching strategy.**
Trunk-based with short-lived feature branches: branch from main, keep it under a few days, rebase onto main before the PR, squash-merge back, delete the branch. Tags mark releases. I avoid long-lived develop and release branches for most products because the merge overhead outweighs the benefit — Gitflow makes sense when you genuinely ship versioned releases to customers who stay on old versions.

**Q24. What makes a good commit message?**
A conventional-commit prefix, imperative mood, subject under about 50 characters, and a body explaining *why* when it is not obvious. `fix(login): handle slow redirect causing flake` tells me what changed and why in one line. The test is whether someone debugging in six months can understand the change without opening the diff.

**Q25. How small should a commit be?**
One logical change — revertable on its own without breaking anything. If I cannot describe it in one sentence without "and", it should be split. This is not aesthetics: `revert` and `bisect` both depend on commits being atomic, and a bisect that lands on a 600-file commit tells you nothing useful.

**Q26. Squash merge, merge commit, or rebase merge?**
Squash for most feature PRs — one PR becomes one clean commit on main, which keeps main readable and bisectable. Merge commit when the intermediate history is genuinely valuable or for an auditable release merge. Rebase merge for linear history without merge commits, though it loses the record that the work was grouped. The team should pick one and enforce it in branch settings rather than leaving it to individual judgement.

**Q27. What goes in `.gitignore` for a test automation repo?**
`node_modules`, build output, `test-results`, `playwright-report`, `blob-report`, Python `.venv` and `__pycache__`, and critically `.env` files and saved Playwright `storageState` JSON — those hold live credentials and sessions. I commit a `.env.example` listing the keys with no values so onboarding is still easy.

**Q28. How do you keep a long-running branch from becoming a merge nightmare?**
Rebase onto main daily, and if it is going to live more than a few days, question whether the work can be split behind a feature flag and merged incrementally. Conflict pain grows with the square of how long you wait, so the real fix is branch lifetime, not better conflict-resolution skill.

**Q29. What are Git hooks and have you used them?**
Scripts Git runs at lifecycle points. `pre-commit` for lint, format, and secret scanning; `commit-msg` to enforce the message convention; `pre-push` to run a fast test subset. They live in `.git/hooks`, which is not versioned, so teams use Husky or pre-commit to share them. Keep them fast — a `pre-commit` that takes 30 seconds gets bypassed with `--no-verify`, and then it protects nothing.

**Q30. What is `git worktree` and when is it better than stashing?**
It checks out another branch into a separate directory sharing the same `.git`. Better than stashing whenever the interruption will last more than a few minutes: both working states stay intact, and you do not lose a warm build or dev server. I use it for hotfixes and for reviewing a PR while my own work is mid-flight.

**Q31. How does Git fit into your CI pipeline?**
Push or PR triggers the pipeline via webhook. PRs run lint, typecheck, and an affected or smoke test subset; main runs the full suite; nightly runs everything including long jobs. Branch protection requires passing checks and a review before merge, and blocks force-push to main. For CI checkouts I use shallow clones for speed unless the job needs history.

**Q32. Have you used `git bisect` or the reflog in a real situation?**
Yes to both — and these are the two answers worth having a specific story for. Bisect with `--repeat-each` to locate a commit that introduced flakiness. Reflog to recover commits after a bad `reset --hard` and after deleting an unmerged branch. Both are the difference between "I know Git commands" and "I have got myself out of trouble with Git."

---

# 19. Quick reference card

## Most used

```bash
git status -sb
git add -p
git commit -m "type(scope): message"
git push
git pull --rebase
git switch -c feature/name
git log --oneline --graph --decorate --all
git diff --staged
```

## Undo, by situation

```bash
git restore file.ts               # discard my edit
git restore --staged file.ts      # unstage, keep edit
git commit --amend --no-edit      # add to last commit
git reset --soft HEAD~1           # undo commit, keep staged
git reset --hard HEAD~1           # undo commit, destroy changes
git revert <sha>                  # undo a PUSHED commit
git reflog                        # find anything lost
```

## Investigate

```bash
git log -S "searchString"         # when did this code change?
git log --grep="keyword"          # search messages
git blame -L 10,20 file.ts        # who wrote these lines
git show HEAD~3:path/file.ts      # file as it was then
git bisect run <test command>     # what broke this?
git log main..feature             # what am I proposing?
```

## Fix common problems

```bash
git pull --rebase                       # diverged branches
git merge --abort                       # escape a bad merge
git rebase --abort                      # escape a bad rebase
git switch -c saved                     # rescue detached HEAD
git rm --cached .env                    # stop tracking a file
git clean -n                            # preview untracked deletion
git push --force-with-lease             # safe force push
git fetch --all --prune                 # clean stale remote branches
```

## The five rules

1. `git status` before and after anything you are unsure about.
2. Never rewrite history that has left your machine — use `revert`.
3. `--force-with-lease`, never plain `--force`.
4. `git clean -n` before `git clean -f`, every time.
5. Nothing is truly lost until garbage collection — check `git reflog` before panicking.
