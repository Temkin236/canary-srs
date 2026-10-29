# Contributing to Canary SRS

Thank you for contributing to Canary SRS.

## Development Workflow
1. **Branching**: Branch off `main` using standard prefixes:
   - `feat/feature-name`
   - `fix/bug-fix`
   - `test/test-addition`
   - `docs/documentation-update`
   - `chore/tooling-or-maintenance`
2. **Commit Messages**: Follow Conventional Commits format:
   - `feat: implement duplicate detection algorithm`
   - `fix: sanitize CSV formulas against injection`
   - `test: verify bounded typo matching in markers`
   - `docs: update requirements traceability matrix`
3. **Pull Requests**:
   - Provide a clear PR title and description.
   - Link any relevant requirements or issues.
   - Ensure all CI tests (frontend build/tests, backend tests/linting) pass.

## Local Setup
### Backend
```bash
cd backend
mise exec -- uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
ruff check .
```

### Frontend
```bash
cd frontend
npm install
npm run test
npm run build
```
