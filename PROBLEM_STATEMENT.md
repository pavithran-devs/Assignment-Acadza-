# Acadza AI Intern Assignment

## The Problem

Acadza is an EdTech platform for students preparing for JEE and NEET. We track every test, assignment, and practice session — questions attempted, time spent, marks scored, what was skipped, what was aborted.

Build a recommender system that takes a student's performance data across multiple sessions and recommends what to present to them next — step by step, with specific questions for each step.

---

## DOSTs

DOST = Dynamic Optimized Study Task. These are the learning activities Acadza offers:

| DOST Type | What it is |
|-----------|-----------|
| `practiceTest` | Full timed mock test, exam simulation |
| `practiceAssignment` | Targeted problem set, no timer |
| `formula` | Formula revision sheet for chapters |
| `revision` | Multi-day revision plan with daily schedule |
| `concept` | Theory and conceptual explanation |
| `clickingPower` | Speed drill — 10 rapid-fire questions |
| `pickingPower` | MCQ option elimination practice |
| `speedRace` | Competitive timed race against bot |

Parameters and configuration for each DOST are in `dost_config.json`.

---

## Data

### `student_performance.json` — 10 students, 5-8 sessions each

```json
{
  "attempt_id": "ATT_001_03",
  "date": "2026-03-20",
  "mode": "test",
  "exam_pattern": "mains",
  "subject": "Physics",
  "chapters": ["Thermodynamics", "Heat Transfer"],

  "duration_minutes": 60,
  "time_taken_minutes": 62,
  "completed": true,

  "total_questions": 25,
  "attempted": 25,
  "skipped": 0,

  "question_type_split": {"scq": 20, "integer": 5},
  "attempted_type_split": {"scq": 20, "integer": 5},

  "marks": "+52 -8",

  "avg_time_per_question_seconds": 149,
  "slowest_question_id": "Q_PHY_0042",
  "slowest_question_time_seconds": 390,
  "fastest_question_id": "Q_PHY_0091",
  "fastest_question_time_seconds": 28
}
```

Notes:
- `mode`: `"test"` (timed) or `"assignment"` (untimed). `duration_minutes` is `null` for assignments.
- `completed`: whether the student finished or aborted mid-run.
- `marks`: intentionally inconsistent format across attempts — `"68/100"`, `"28"`, `"+52 -12"`, `"34/75 (45.3%)"`, `72`. Normalize it.
- Outlier question IDs reference questions in `question_bank.json`.

### `question_bank.json` — 200 questions

```json
{
  "_id": {"$oid": "5fca00cece6b0b0563640a51"},
  "questionType": "scq",
  "subject": "Physics",
  "topic": "kinematics",
  "subtopic": "projectile_motion",
  "difficulty": 3,
  "scq": {
    "question": "<h3>A projectile is fired at 45°...</h3><h3>(A) 20 m/s<br />(B) 25 m/s<br />(C) 30 m/s<br />(D) 35 m/s</h3>",
    "solution": "<h3>Using the range formula...</h3>",
    "answer": "B"
  }
}
```

- `_id` in two formats: `{"$oid": "..."}` or flat string. Handle both.
- Types: `scq`, `mcq`, `integerQuestion`
- ~10% have issues (missing answer, null difficulty, duplicate _id).

### `dost_config.json` — DOST type definitions and parameters

---

## Endpoints

Build a **FastAPI** application:

### `POST /analyze/{student_id}`

Analyze a student's performance across all sessions. Return patterns, trends, chapter-wise breakdown, strengths, weaknesses.

### `POST /recommend/{student_id}`

Return a step-by-step plan:

**Step 1:** DOST type, target chapter, parameters (from config), specific question IDs from the bank.
**Step 2:** ...
**Step N:** ...

Each step includes reasoning and a message to the student.

### `GET /question/{question_id}`

Look up a question. Normalize `_id`. Return clean data with plaintext preview.

### `GET /leaderboard`

Rank all 10 students. Design a scoring formula. Show rank, score, strength, weakness, focus area.

---

## Sample Outputs

Run `/analyze` and `/recommend` on all 10 students. Save outputs in `sample_outputs/`.

---

## Debug Task (30%)

`debug/recommender_buggy.py` — a buggy recommendation engine. It runs without errors but produces wrong results. Find the root cause, fix it, explain what went wrong.

AI tools are allowed. The bug is designed to fool them.

---

## Deliverables

1. Working FastAPI project with `requirements.txt` and setup instructions.
2. `sample_outputs/` — all 10 students analyzed + recommended.
3. Debug fix — corrected file.
4. **README (in your own words, minimum 500 words)** covering:
   - Your approach to the build task — how you analyzed student data, how you decided which DOSTs to recommend and in what order.
   - How you handled the messy marks field and any assumptions you made.
   - Your debug process — what the bug was, how you found it, what you tried that didn't work, what AI suggested if you used it.
   - What you'd improve given more time.

Write the README yourself. It matters.

## Rules

- **Deadline:** Monday 6th April 2026, 9:00 PM IST. Late = not reviewed.
- **AI usage:** Allowed. Encouraged.
- **Submit:** Reply with GitHub link.
