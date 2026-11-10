# Detection Methodology & Human Review Guidelines

Canary SRS employs **four deterministic, explainable evidence checks** to uncover potential LLM contamination in crowd-annotated datasets. In keeping with Canary's core philosophy—**"Evidence, Not Verdict"**—none of these checks provide definitive proof of AI generation or cheating. They serve as structured, calibrated signals to guide human stewards.

---

## Modality 1: Hidden Task-Specific Canary Marker Echoes

### Concept & Preparation
A cryptographically pseudorandom canary token (e.g., `cnry_7f2b9a`, 256 bits of entropy) is seeded into task prompt instructions before task distribution to workers.

### Injection Techniques
1. **Zero-Width Unicode Sequence**:
   - The token is encoded into invisible Unicode non-printable characters (`\u200b` ZERO WIDTH SPACE, `\u200c` ZERO WIDTH NON-JOINER, `\u200d` ZERO WIDTH JOINER).
   - Invisible to human workers in web UI rendering, but copied into clipboard buffers upon copy-paste.
   - When pasted into a chatbot, the LLM incorporates the hidden sequence into its attention window and frequently echoes the sequence into its generated completion.
2. **Subtle Instruction Footnotes**:
   - A subtle constraint embedded in prompt guidelines directing reference to an alphanumeric code.

### Matching Algorithm & Thresholds
- **Exact Match**: Case-insensitive substring match against the known marker manifest.
- **Bounded Edit-Distance**: Levenshtein distance $d \le 1$ for tokens of length $\ge 8$ characters, accounting for minor chatbot token boundary alterations.

$$\text{Confidence} = \begin{cases} \text{High} & \text{if } d(\text{echo}, \text{marker}) = 0 \\ \text{Medium} & \text{if } 0 < d(\text{echo}, \text{marker}) \le 1 \\ \text{None} & \text{otherwise} \end{cases}$$

### Limitations
- Workers who manually retype prompts will not copy the invisible marker.
- Aggressive upstream text normalization pipelines or OCR can strip zero-width codepoints.

---

## Modality 2: AI Reference Similarity & Peer Distribution Contextualization

### Concept
Measuring lexical and semantic overlap between a worker's submission and reference answers generated for the task. Crucially, raw similarity is never evaluated in a vacuum—it is contextualized by the **peer distribution** of all answers submitted for that specific task.

### Algorithm
1. **TF-IDF Vectorization**: Extract character 3-grams and word n-grams ($n \in [1, 2]$).
2. **Cosine Similarity**:

$$\text{sim}_{\text{cos}}(A, R) = \frac{\vec{A} \cdot \vec{R}}{\|\vec{A}\| \|\vec{R}\|}$$

3. **Peer Percentile Ranking**:
   For task $T$ with submissions $A_1, A_2, \dots, A_m$, compute the empirical cumulative distribution function (ECDF):

$$\text{Percentile}(A_i) = \frac{1}{m} \sum_{j=1}^m \mathbf{1}\left(\text{sim}(A_j, R) \le \text{sim}(A_i, R)\right) \times 100$$

### Thresholds & Scoring
- **Elevated Finding**: $\text{sim}_{\text{cos}} \ge 0.82$ AND $\text{Percentile} \ge 95.0\%$.
- **High Confidence**: Requires concurrent finding in another modality (e.g. peer duplication or marker echo).
- **Small Peer Group Guard**: If $m < 5$, Canary flags the peer group as statistically underpowered and caps confidence at Low.

### Limitations
- Standard factual definitions (e.g. "What is photosynthesis?") naturally converge on identical terminology across legitimate human writers.

---

## Modality 3: Cross-Worker Duplicate Clustering

### Concept
Detecting identical or near-verbatim answer text submitted across distinct `worker_id` accounts for the same `task_id`.

### Algorithm
1. **Exact Token Hashing**: Computes SHA-256 digest of normalized token sequences to surface 100% identical duplicates.
2. **Token 3-Gram Jaccard Similarity**:

$$J(S_1, S_2) = \frac{|S_1 \cap S_2|}{|S_1 \cup S_2|}$$

where $S_1, S_2$ are sets of word 3-grams.
3. **MinHash Locality-Sensitive Hashing (LSH)**: Used for rapid $O(N)$ candidate pair generation across large datasets ($N > 10,000$).

### Thresholds
- **Verbatim Duplicate**: $J = 1.0$ (High Confidence when answer length $> 25$ characters).
- **Near-Verbatim Cluster**: $0.80 \le J < 1.0$ (Medium Confidence).

### Limitations
- Very brief responses (e.g. single numbers, "Yes/No", country names) will naturally produce high Jaccard scores. Canary applies a minimum character length guard ($L \ge 30$ chars) before triggering near-duplicate alerts.

---

## Modality 4: Typing Velocity & Submission Speed Plausibility

### Concept
Evaluates the physical plausibility of manual typing speed when client submission timestamps (`seconds_spent` or `submitted_at`) are available in the dataset.

### Metric

$$\text{Velocity} = \frac{\text{Character Count}}{\text{Seconds Spent}} \quad (\text{chars/sec})$$

### Thresholds
- **Plausible Human Speed**: $\le 10 \text{ chars/sec}$ (approx. 120 words per minute).
- **Extreme Velocity Anomaly**: $> 15 \text{ chars/sec}$ (sustained manual typing exceeding 180 words per minute).
- **Confidence**: Capped at **Low/Medium**—speed alone is never sufficient for an adverse finding.

### Limitations
- Workers often draft long answers in local word processors or IDEs and paste them into the task form in a single action. High velocity demonstrates paste behavior, not necessarily LLM generation.

---

## Reviewer Interpretation Matrix

| Modality Combination | Recommended Reviewer Interpretation |
|---|---|
| **Marker Echo Alone** | High probability that task prompt was pasted into an external LLM interface. Review worker instructions. |
| **Marker Echo + High Speed** | Strong evidence of direct copy-paste workflow from external prompt execution. |
| **High Similarity + Peer Duplicate** | Strong evidence of answer sharing, syndicated accounts, or identical external LLM prompt completions. |
| **High Similarity Alone** | Inconclusive without marker or duplicate corroboration; frequently benign domain convergence. |
| **High Speed Alone** | Weak evidence; often indicates external offline drafting. |
