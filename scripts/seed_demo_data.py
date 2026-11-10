#!/usr/bin/env python3
"""
Seeds canary.db with realistic development fixture data for demonstration,
reviewer dashboard analytics, and authentic screenshot capture.
"""

import datetime
import os
import sys
import uuid

# Ensure backend is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.security import hash_secret_token
from app.db.session import Base, SessionLocal, engine
from app.models.audit import (
    Audit,
    AuditAnswer,
    CheckResult,
    Finding,
    FindingReviewHistory,
    JobState,
    Marker,
    ReferenceAnswer,
)


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        expires = now + datetime.timedelta(days=7)

        # 1. Primary Showcase Audit
        primary_secret = "sec_demo_review_2026_canary"
        primary_token_hash = hash_secret_token(primary_secret)
        primary_audit_id = "canary-audit-demo-8492"

        # Check if already seeded
        existing = db.query(Audit).filter(Audit.id == primary_audit_id).first()
        if existing:
            print(f"Audit {primary_audit_id} already exists. Cleaning up before re-seed...")
            db.delete(existing)
            db.commit()

        audit = Audit(
            id=primary_audit_id,
            token_hash=primary_token_hash,
            status="completed",
            answers_count=24,
            workers_count=10,
            flagged_workers_count=3,
            consent_external_ai=False,
            dataset_name="crowd_eval_batch_october.csv",
            created_at=now - datetime.timedelta(hours=3),
            completed_at=now - datetime.timedelta(hours=2, minutes=45),
            expires_at=expires,
            summary_metrics={
                "marker_findings": 2,
                "similarity_findings": 3,
                "duplicate_findings": 2,
                "speed_findings": 1,
                "total_flagged": 4,
            },
        )
        db.add(audit)

        job_state = JobState(
            id=str(uuid.uuid4()),
            audit_id=primary_audit_id,
            stage="completed",
            progress_percentage=100,
            current_check="completed",
            started_at=now - datetime.timedelta(hours=3),
            last_heartbeat=now - datetime.timedelta(hours=2, minutes=45),
        )
        db.add(job_state)

        # Tasks and Answers
        tasks_data = [
            {
                "task_id": "task_bio_101",
                "prompt": "Explain the role of chloroplasts in eukaryotic plant cells.",
                "ref": "Chloroplasts are specialized plant organelles that conduct photosynthesis, absorbing sunlight with chlorophyll pigments to synthesize chemical energy (glucose) from water and carbon dioxide.",
                "marker": "cnry_chlp_8492",
                "answers": [
                    {
                        "worker_id": "worker_07",
                        "answer": "Chloroplasts conduct photosynthesis by converting solar photons into chemical sugar bonds using chlorophyll. \u200b\u200c\u200dcnry_chlp_8492 They maintain a double membrane and contain thylakoid discs.",
                        "sec": 14.5,
                        "flag": "marker",
                    },
                    {
                        "worker_id": "worker_12",
                        "answer": "Chloroplasts conduct photosynthesis by converting solar photons into chemical sugar bonds using chlorophyll. \u200b\u200c\u200dcnry_chlp_8492 They maintain a double membrane and contain thylakoid discs.",
                        "sec": 12.0,
                        "flag": "duplicate",
                    },
                    {
                        "worker_id": "worker_31",
                        "answer": "Chloroplasts are plant cell organelles carrying out photosynthesis. They capture light energy and produce energy storage molecules like ATP and NADPH while releasing oxygen.",
                        "sec": 165.0,
                        "flag": "clean",
                    },
                    {
                        "worker_id": "worker_88",
                        "answer": "These organelles absorb sunlight and convert it into glucose to feed the plant cell during daytime hours.",
                        "sec": 95.0,
                        "flag": "clean",
                    },
                ],
            },
            {
                "task_id": "task_cs_204",
                "prompt": "Compare depth-first search and breadth-first search graph traversal algorithms.",
                "ref": "Depth-first search (DFS) traverses down graph branches using a stack (or recursion) before backtracking, using O(V) memory. Breadth-first search (BFS) explores neighbor nodes layer-by-layer using a FIFO queue, finding the shortest unweighted path with O(V+E) time.",
                "marker": "cnry_algo_7104",
                "answers": [
                    {
                        "worker_id": "worker_42",
                        "answer": "DFS uses a LIFO stack or recursive call stack to dive down paths until dead ends are reached, whereas BFS uses a FIFO queue to visit adjacent vertices level by level. BFS guarantees shortest path in unweighted graphs.",
                        "sec": 8.0,
                        "flag": "speed",
                    },
                    {
                        "worker_id": "worker_99",
                        "answer": "Depth-first search traverses along graph paths using recursion/stack before backtracking. In contrast, BFS visits immediate neighboring vertices layer by layer utilizing a queue structure.",
                        "sec": 140.0,
                        "flag": "similarity",
                    },
                    {
                        "worker_id": "worker_55",
                        "answer": "DFS goes deep down one branch before exploring others, while BFS checks all neighbor nodes first before moving deeper into the graph.",
                        "sec": 110.0,
                        "flag": "clean",
                    },
                ],
            },
            {
                "task_id": "task_hist_308",
                "prompt": "Describe the economic impact of the Silk Road during the Han Dynasty.",
                "ref": "The Silk Road established trans-Eurasian trade networks linking China with Central Asia, Persia, and the Roman Empire, fostering commercial exchange in silk, spices, glassware, and technological diffusion.",
                "marker": "cnry_silk_3311",
                "answers": [
                    {
                        "worker_id": "worker_23",
                        "answer": "The Silk Road facilitated commercial trade between China and Western civilizations, exporting Chinese silk, porcelain, and tea while importing horses, silver, and Mediterranean glassware.",
                        "sec": 180.0,
                        "flag": "clean",
                    },
                    {
                        "worker_id": "worker_12",
                        "answer": "The Silk Road facilitated commercial trade between China and Western civilizations, exporting Chinese silk, porcelain, and tea while importing horses, silver, and Mediterranean glassware.",
                        "sec": 22.0,
                        "flag": "duplicate",
                    },
                ],
            },
        ]

        answers_map = {}
        for t in tasks_data:
            # Marker
            marker = Marker(
                id=str(uuid.uuid4()),
                audit_id=primary_audit_id,
                task_id=t["task_id"],
                marker_token=t["marker"],
                hiding_method="zero_width",
            )
            db.add(marker)

            # Ref answer
            ref = ReferenceAnswer(
                id=str(uuid.uuid4()),
                audit_id=primary_audit_id,
                task_id=t["task_id"],
                provider="offline-synthetic",
                model_name="synthetic-reference-v1",
                reference_text=t["ref"],
            )
            db.add(ref)

            # Answers
            for a in t["answers"]:
                ans_id = str(uuid.uuid4())
                audit_answer = AuditAnswer(
                    id=ans_id,
                    audit_id=primary_audit_id,
                    task_id=t["task_id"],
                    worker_id=a["worker_id"],
                    prompt=t["prompt"],
                    answer=a["answer"],
                    submitted_at=now - datetime.timedelta(minutes=30),
                    seconds_spent=a["sec"],
                )
                db.add(audit_answer)
                answers_map[(t["task_id"], a["worker_id"])] = (ans_id, audit_answer, a)

        db.commit()

        # Findings
        # 1. Marker Finding
        ans_id, ans_obj, a_data = answers_map[("task_bio_101", "worker_07")]
        f1 = Finding(
            id="find-marker-001",
            audit_id=primary_audit_id,
            answer_id=ans_id,
            task_id="task_bio_101",
            worker_id="worker_07",
            check_identifier="check_marker",
            finding_type="Hidden Canary Marker Echo",
            evidence_confidence="High",
            explanation="Exact zero-width canary token 'cnry_chlp_8492' seeded in task prompt was echoed in submitted answer.",
            evidence_text="[Zero-Width Unicode Marker: cnry_chlp_8492]",
            evidence_offsets=[97, 128],
            numerical_measurements={"edit_distance": 0, "token_match": 1.0},
            limitations="Evidence for human review only; marker echoes indicate prompt insertion into external software.",
            review_status="under_review",
            reviewer_notes="Confirmed invisible Unicode character sequence matches prompt injection token. Requesting reviewer confirmation.",
            assigned_reviewer="Temkin Abdulmelik",
        )
        db.add(f1)

        # 2. Duplicate Finding
        ans_id2, ans_obj2, a_data2 = answers_map[("task_bio_101", "worker_12")]
        f2 = Finding(
            id="find-dup-002",
            audit_id=primary_audit_id,
            answer_id=ans_id2,
            task_id="task_bio_101",
            worker_id="worker_12",
            check_identifier="check_duplicate",
            finding_type="Cross-Worker Verbatim Duplicate",
            evidence_confidence="High",
            explanation="Answer is 100% character-identical to submission by worker_07 for the same task.",
            evidence_text=a_data2["answer"],
            numerical_measurements={"jaccard_3gram": 1.0, "minhash_similarity": 1.0},
            related_answer_ids=[ans_id],
            limitations="Duplicate answers show text reuse across accounts; requires reviewer context on team submissions.",
            review_status="needs_investigation",
            reviewer_notes="Identical answer text across worker_07 and worker_12 on task_bio_101.",
            assigned_reviewer="Temkin Abdulmelik",
        )
        db.add(f2)

        # 3. Speed / Velocity Finding
        ans_id3, ans_obj3, a_data3 = answers_map[("task_cs_204", "worker_42")]
        f3 = Finding(
            id="find-speed-003",
            audit_id=primary_audit_id,
            answer_id=ans_id3,
            task_id="task_cs_204",
            worker_id="worker_42",
            check_identifier="check_speed",
            finding_type="Typing Velocity Anomaly",
            evidence_confidence="Medium",
            explanation="Submission speed calculated at 28.5 characters per second (228 chars in 8.0s), exceeding human typing threshold (15 chars/sec).",
            evidence_text=a_data3["answer"][:100] + "...",
            numerical_measurements={"chars_per_second": 28.5, "seconds_spent": 8.0, "total_chars": 228},
            limitations="Plausibility indicator only; does not distinguish fast copy-paste from drafting in external text editor.",
            review_status="pending_review",
            reviewer_notes=None,
        )
        db.add(f3)

        # 4. Peer Similarity Finding
        ans_id4, ans_obj4, a_data4 = answers_map[("task_cs_204", "worker_99")]
        f4 = Finding(
            id="find-sim-004",
            audit_id=primary_audit_id,
            answer_id=ans_id4,
            task_id="task_cs_204",
            worker_id="worker_99",
            check_identifier="check_similarity",
            finding_type="Elevated Reference Similarity",
            evidence_confidence="Medium",
            explanation="TF-IDF cosine similarity of 0.88 against reference answer, ranking in the 98.4th percentile of task answers.",
            evidence_text=a_data4["answer"],
            numerical_measurements={"cosine_similarity": 0.88, "peer_percentile": 98.4},
            limitations="Statistical lexical overlap only; legitimate human explanations often share standard technical terms.",
            review_status="reviewed",
            reviewer_notes="Standard vocabulary explanation of BFS/DFS. Evidence reviewed and cataloged.",
            assigned_reviewer="Temkin Abdulmelik",
            reviewed_at=now - datetime.timedelta(minutes=15),
        )
        db.add(f4)

        # Add additional audits for Dashboard diversity
        audit2 = Audit(
            id="canary-audit-legal-5120",
            token_hash=hash_secret_token("sec_legal_audit_token_demo"),
            status="completed",
            answers_count=48,
            workers_count=16,
            flagged_workers_count=2,
            consent_external_ai=False,
            dataset_name="legal_contract_clauses_round1.csv",
            created_at=now - datetime.timedelta(days=1, hours=4),
            completed_at=now - datetime.timedelta(days=1, hours=3, minutes=40),
            expires_at=expires - datetime.timedelta(days=1),
            summary_metrics={"marker_findings": 1, "similarity_findings": 2, "duplicate_findings": 1, "speed_findings": 0},
        )
        db.add(audit2)

        audit3 = Audit(
            id="canary-audit-medical-3049",
            token_hash=hash_secret_token("sec_medical_qa_token_demo"),
            status="completed",
            answers_count=120,
            workers_count=28,
            flagged_workers_count=4,
            consent_external_ai=False,
            dataset_name="clinical_qa_transcriptions.jsonl",
            created_at=now - datetime.timedelta(days=2),
            completed_at=now - datetime.timedelta(days=2, hours=-1),
            expires_at=expires - datetime.timedelta(days=2),
            summary_metrics={"marker_findings": 3, "similarity_findings": 4, "duplicate_findings": 3, "speed_findings": 2},
        )
        db.add(audit3)

        db.commit()
        print(f"Successfully seeded demo audits!")
        print(f"Primary Audit ID: {primary_audit_id}")
        print(f"Primary Audit Secret: {primary_secret}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
