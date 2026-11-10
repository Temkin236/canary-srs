## Description
<!-- Provide a concise explanation of the changes made and the motivation behind them. -->

## Associated Requirements & Invariants
<!-- Reference relevant requirements (e.g., FR-1 to FR-46) or core invariants. -->
- [ ] Invariant 1: Evidence, Not Verdict (Does not claim definitive proof of AI generation or cheating)
- [ ] Invariant 2: No Automated Punishment (Never rejects or penalizes workers automatically)
- [ ] Invariant 3: Zero Stylometric Hallucination (Deterministic evidence only, no uncalibrated perplexity)
- [ ] Invariant 4: Privacy & Explicit Consent (No external AI transmission without opt-in)
- [ ] Invariant 5: No Secret Leakage (Raw secret tokens never logged or stored unhashed)
- [ ] Invariant 6: Deterministic Offline Capability (Runs fully without internet/external AI)

## Type of Change
- [ ] `feat`: New feature or capability
- [ ] `fix`: Bug fix
- [ ] `test`: New or updated tests
- [ ] `docs`: Documentation updates or additions
- [ ] `chore`: Maintenance, dependencies, or tooling
- [ ] `perf`: Performance improvement

## Testing & Verification
<!-- Describe the tests executed and attach proof of verification. -->
- Backend tests: `uv run --project backend pytest backend/tests/`
- Backend linting: `uv run --project backend ruff check backend/`
- Frontend tests: `npm --prefix frontend test -- --run`
- Frontend typecheck: `npm --prefix frontend run typecheck`
- Frontend build: `npm --prefix frontend run build`

## Checklist
- [ ] Code adheres to project style guidelines (Ruff for Python, ESLint/TypeScript for frontend)
- [ ] All new and existing tests pass locally
- [ ] Documentation updated to reflect changes
