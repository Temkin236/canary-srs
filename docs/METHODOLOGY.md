# Methodology & Limitations — Canary SRS

## Objective
Canary SRS provides dataset stewards and researchers with structured, explainable evidence when investigating potential chatbot contamination in human-written crowd tasks.

## Core Detection Modalities

### 1. Task-Specific Marker Injection & Detection
- **Mechanism**: Unique, cryptographically pseudo-random canary markers (e.g., `cnry_9a8f21`) are embedded in task instructions.
- **Hiding Techniques**:
  - *Zero-Width Non-Joiner / Joiner Unicode sequence*: Invisible to human readers in standard rendering, but copied into clipboard buffers.
  - *Embedded Prompt Constraint*: Subtle syntactic instruction (e.g. including a canary token in a reference footnote).
- **Matching Algorithm**:
  - Exact match (normalized whitespace/casing).
  - Fuzzy typo tolerance (bounded Levenshtein distance $\le 1$ or $\le 2$ on tokens $> 6$ characters).
- **Evidence Confidence**: High.
- **Limitations**: If a crowd worker manually retypes the question rather than copying and pasting, hidden markers will not be transferred to the chatbot prompt.

### 2. Similarity to AI Reference Outputs & Peer Distributions
- **Mechanism**: Canary generates reference answers using specified models and compares each crowd answer against:
  1. The reference answers.
  2. The distribution of answers submitted by all other workers for the same task.
- **Metric**: Combined TF-IDF lexical n-gram cosine similarity and sentence embedding cosine similarity.
- **Interpretation Rule**:
  - Raw high similarity alone is not sufficient evidence of contamination, as simple factual questions naturally elicit near-identical responses across human writers.
  - Canary measures the *percentile rank* within the peer group. If a worker's answer is in the top 1% similarity to AI output *and* exhibits near-copy overlap with a peer, confidence is escalated.
- **Limitations**: Small peer groups (< 5 answers) lack statistical power to compute reliable percentiles; Canary explicitly flags small peer groups as insufficient evidence.

### 3. Cross-Worker Duplicate Detection
- **Mechanism**: Checks for identical or near-identical answers across distinct `worker_id`s for the same `task_id`.
- **Metric**: Token 3-gram Jaccard similarity and character sequence overlap.
- **Evidence Confidence**: Medium (near-duplicate) to High (near-duplicate combined with model similarity).
- **Limitations**: Common idioms, boilerplate text, or brief factual responses (e.g., "Paris") will naturally yield duplicate matches; reviewers must consider response length.

### 4. Speed & Typing Velocity Plausibility
- **Mechanism**: When `seconds_spent` metadata is provided, Canary computes typing velocity (characters per second).
- **Plausibility Threshold**: Default threshold is 15 characters per second (approx. 180 words per minute sustained). Answers exceeding this rate are flagged as implausibly fast for manual typing.
- **Evidence Confidence**: Low (speed alone is never sufficient for a high-confidence finding).
