# Publishing chengeta-ai

Step-by-step guide to publish on **GitHub**, **PyPI** (pip), **uv**, and **conda-forge**.

---

## 1. GitHub

### First-time setup

```bash
cd d:/Github/chengeta-ai

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: chengeta-ai v0.1.0"

# Option A: Using GitHub CLI (recommended)
gh repo create chengeta-ai --public --source=. --push --description "Unified caching layer for AI/agent frameworks"

# Option B: Manual
# 1. Go to https://github.com/new → create "chengeta-ai"
# 2. Then:
git remote add origin https://github.com/vigilancetrent/chengeta-ai.git
git branch -M main
git push -u origin main
```

### After pushing

1. Go to your repo → **Settings → Pages** → set source to `main` branch (optional, for docs)
2. Go to **Settings → Environments** → create two environments:
   - `testpypi` — for TestPyPI publishing
   - `pypi` — for production PyPI publishing
3. The CI workflow ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs automatically on every push/PR
4. The publish workflow ([.github/workflows/publish.yml](.github/workflows/publish.yml)) runs when you create a GitHub Release

### Creating a release

```bash
# Tag the version
git tag v0.1.0
git push origin v0.1.0

# Create release via CLI
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release — see CHANGELOG.md"

# Or create via GitHub UI:
# Go to Releases → Draft a new release → Choose tag v0.1.0 → Publish
```

---

## 2. PyPI (pip install)

### One-time setup (Trusted Publishing — recommended, no API tokens needed)

1. Create accounts on:
   - https://pypi.org/account/register/
   - https://test.pypi.org/account/register/

2. **Configure Trusted Publishing on PyPI:**
   - Go to https://pypi.org/manage/account/publishing/
   - Click **"Add a new pending publisher"**
   - Fill in:
     - PyPI project name: `chengeta-ai`
     - Owner: `vigilancetrent`
     - Repository: `chengeta-ai`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`
   - Click **"Add"**

3. **Do the same on TestPyPI:**
   - Go to https://test.pypi.org/manage/account/publishing/
   - Same fields, but environment name: `testpypi`

4. **Configure GitHub environments:**
   - Go to your repo → Settings → Environments
   - Create `pypi` environment (optionally add approval requirement for safety)
   - Create `testpypi` environment

### Publishing (automatic)

Once trusted publishing is configured, just create a GitHub Release (see above). The workflow will:
1. Build the package
2. Publish to TestPyPI
3. Publish to PyPI

### Publishing (manual — for testing)

```bash
# Build
uv build
# This creates dist/chengeta_ai-0.1.0.tar.gz and dist/chengeta_ai-0.1.0-py3-none-any.whl

# Upload to TestPyPI first
uv publish --publish-url https://test.pypi.org/legacy/
# Enter your TestPyPI API token when prompted

# Verify it works
pip install -i https://test.pypi.org/simple/ chengeta-ai

# Upload to production PyPI
uv publish
# Enter your PyPI API token when prompted

# Alternative: use twine
pip install twine
twine upload dist/*
```

### After publishing

```bash
# Users can now install with:
pip install chengeta-ai                     # core only
pip install 'chengeta-ai[redis]'            # with Redis
pip install 'chengeta-ai[langchain]'        # with LangChain
pip install 'chengeta-ai[all]'              # everything
```

---

## 3. uv (uv add / uv pip install)

**No extra steps needed!** uv installs directly from PyPI. Once your package is on PyPI:

```bash
# Users install with:
uv add chengeta-ai                          # add to project
uv add 'chengeta-ai[langchain,redis]'       # with extras
uv pip install chengeta-ai                  # pip-style install

# From git (even before PyPI release):
uv add git+https://github.com/vigilancetrent/chengeta-ai
uv pip install git+https://github.com/vigilancetrent/chengeta-ai
```

uv reads `pyproject.toml` natively — no additional configuration required.

---

## 4. conda-forge (conda install)

### Submitting to conda-forge

conda-forge is community-maintained. After your **first PyPI release**:

1. **Fork the conda-forge staged-recipes repo:**
   ```bash
   gh repo fork conda-forge/staged-recipes --clone
   cd staged-recipes
   ```

2. **Copy your recipe:**
   ```bash
   mkdir -p recipes/chengeta-ai
   cp /path/to/chengeta-ai/conda-recipe/meta.yaml recipes/chengeta-ai/meta.yaml
   ```

3. **Update the sha256 hash** in `meta.yaml`:
   ```bash
   # Get the hash from PyPI
   curl -sL https://pypi.org/pypi/chengeta-ai/0.1.0/json | python -c "
   import json, sys
   data = json.load(sys.stdin)
   for f in data['urls']:
       if f['filename'].endswith('.tar.gz'):
           print(f['digests']['sha256'])
   "
   ```
   Paste the hash into `meta.yaml` under `source.sha256`.

4. **Replace `vigilancetrent`** in `meta.yaml` with your GitHub username.

5. **Submit PR:**
   ```bash
   git checkout -b add-chengeta-ai
   git add recipes/chengeta-ai/meta.yaml
   git commit -m "Add chengeta-ai recipe"
   git push origin add-chengeta-ai
   gh pr create --repo conda-forge/staged-recipes \
     --title "Add chengeta-ai" \
     --body "New package: chengeta-ai — unified caching layer for AI/agent frameworks.

   - PyPI: https://pypi.org/project/chengeta-ai/
   - GitHub: https://github.com/vigilancetrent/chengeta-ai
   - License: MIT
   - noarch: python"
   ```

6. **Wait for review** — conda-forge bots will build and test your recipe. Reviewers will merge once checks pass (typically 1-3 days).

### After acceptance

```bash
# Users can install with:
conda install -c conda-forge chengeta-ai

# Or with mamba (faster):
mamba install chengeta-ai
```

### Updating versions on conda-forge

After the initial feedstock is created, conda-forge creates a repo `chengeta-ai-feedstock`. When you release a new version on PyPI:
- The conda-forge bot automatically opens a PR to update the version
- Or manually update `meta.yaml` in the feedstock and submit a PR

---

## 5. Version Bump Checklist

When releasing a new version:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

2. **Update `__init__.py`** (if version is defined there):
   ```python
   __version__ = "0.2.0"
   ```

3. **Update CHANGELOG.md** with new entries

4. **Commit and tag:**
   ```bash
   git add -A
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

5. **Create GitHub Release:**
   ```bash
   gh release create v0.2.0 --title "v0.2.0" --notes "See CHANGELOG.md"
   ```

6. The CI/CD pipeline handles the rest (build → TestPyPI → PyPI)
7. conda-forge bot will auto-detect the new PyPI version

---

## Quick Reference

| Platform    | Install command                              | Where it pulls from |
|-------------|----------------------------------------------|---------------------|
| **pip**     | `pip install chengeta-ai`                   | PyPI                |
| **uv**      | `uv add chengeta-ai`                        | PyPI                |
| **conda**   | `conda install -c conda-forge chengeta-ai`  | conda-forge         |
| **git**     | `pip install git+https://github.com/…`       | GitHub              |

| Action                  | Command                                    |
|-------------------------|--------------------------------------------|
| Build locally           | `uv build`                                 |
| Upload to TestPyPI      | `uv publish --publish-url https://test.pypi.org/legacy/` |
| Upload to PyPI          | `uv publish`                               |
| Create GitHub release   | `gh release create v0.1.0`                 |
| Run tests               | `uv run pytest`                            |
| Lint                    | `uv run ruff check .`                      |

---

## Project Structure (publishing-related files)

```
chengeta-ai/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Test + lint on push/PR
│       └── publish.yml         # Publish to PyPI on release
├── conda-recipe/
│   └── meta.yaml               # conda-forge recipe
├── chengeta_ai/
│   ├── __init__.py             # __version__ defined here
│   └── py.typed                # PEP 561 marker
├── .gitignore
├── CHANGELOG.md
├── LICENSE                     # MIT
├── MANIFEST.in                 # sdist includes
├── pyproject.toml              # Package metadata + build config
└── README.md                   # Rendered on PyPI + GitHub
```
