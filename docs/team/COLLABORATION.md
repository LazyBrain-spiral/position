# Team Git & Collaboration Protocol

To maintain FAANG/top-tier engineering speed and hygiene with 4 active contributors:

---

## 1. Branching Strategy (Trunk-Based Development)

All branches branch off `main` (or `develop`) and merge back via Pull Request.

### Branch Naming Conventions:
- `feat/t1-description` -> Platform / Infra changes (Track 1)
- `feat/t2-description` -> Backend API / Engine features (Track 2)
- `feat/t3-description` -> Frontend / Web UI features (Track 3)
- `feat/t4-description` -> Testing, contracts, data curation (Track 4)
- `fix/tX-bug-description` -> Bug fixes
- `chore/tooling-update` -> Build scripts, package updates

---

## 2. Commit Message Standards (Conventional Commits)

Commit messages are enforced by pre-commit hooks and CI:

```
<type>(<scope>): <short description in present tense>

[optional body explaining motivation]

[optional footer: Closes #123]
```

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating test suites
- `docs`: Documentation only changes
- `chore`: Tooling, workflow, or dependency updates

---

## 3. Pull Request Standards

1. PRs must use `.github/PULL_REQUEST_TEMPLATE.md`.
2. Every PR requires at least **1 peer review** approval from an adjacent track.
3. All CI status checks must be green:
   - Ruff linting & formatting
   - Pyright type checking
   - TypeScript `tsc --noEmit`
   - Pytest unit and integration tests
   - Frontend production build verification
4. Always squash and merge to maintain a clean linear commit history.

---

## 4. Track State Isolation

Each contributor updates their designated state tracking file in `docs/state/` at the start and end of every session to prevent work overlap.
