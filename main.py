import json
import os
import re
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any

app = FastAPI(title="Acadza AI Recommender API")
DATA_DIR = "data"

def load_json(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)

students_db = load_json("student_performance.json")
questions_db = load_json("question_bank.json")
dost_db = load_json("dost_config.json")

def parse_marks(marks_val) -> float:
    if isinstance(marks_val, (int, float)):
        return float(marks_val)
    if not marks_val:
        return 0.0
    marks_str = str(marks_val).strip()
    
    # +48 -8
    if '+' in marks_str or ('-' in marks_str and ' ' in marks_str):
        parts = marks_str.split()
        total = 0
        for p in parts:
            try:
                total += float(p)
            except:
                pass
        return float(total)
    
    # 49/120 (40.8%)
    if '/' in marks_str:
        num = marks_str.split('/')[0]
        try:
            return float(num)
        except:
            return 0.0
            
    # just number "22"
    try:
        return float(marks_str)
    except:
        return 0.0

def clean_question_text(html_text: str) -> str:
    if not html_text: return ""
    text = re.sub(r'<[^>]+>', ' ', html_text)
    return ' '.join(text.split())

def normalize_question(_id_val):
    if isinstance(_id_val, dict) and "$oid" in _id_val:
        return _id_val["$oid"]
    return str(_id_val)

def get_student_data(student_id):
    for s in students_db:
        if s["student_id"] == student_id:
            return s
    return None

@app.get("/question/{question_id}")
def get_question(question_id: str):
    for q in questions_db:
        # Check by actual custom 'qid' field which maps to what's in student metrics
        if q.get("qid") == question_id:
            clean_q = dict(q)
            clean_q["_id"] = normalize_question(q.get("_id"))
            
            # Plaintext preview
            q_type = q.get("questionType", "")
            if q_type in q:
                raw_text = q[q_type].get("question", "")
                clean_q["plaintext_preview"] = clean_question_text(raw_text)
            
            return clean_q
    raise HTTPException(status_code=404, detail="Question not found")

@app.post("/analyze/{student_id}")
def analyze_student(student_id: str):
    student = get_student_data(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    chapter_stats = {}
    time_series = []
    total_marks = 0
    total_time = 0
    total_attempted = 0

    for attempt in student.get("attempts", []):
        marks = parse_marks(attempt.get("marks", 0))
        time_series.append({"date": attempt["date"], "marks": marks})
        
        for ch in attempt.get("chapters", []):
            if ch not in chapter_stats:
                chapter_stats[ch] = {"attempts": 0, "marks": 0, "time_taken": 0, "skipped": 0}
            
            chapter_stats[ch]["attempts"] += 1
            chapter_stats[ch]["marks"] += marks
            chapter_stats[ch]["time_taken"] += attempt.get("time_taken_minutes", 0)
            chapter_stats[ch]["skipped"] += attempt.get("skipped", 0)

        total_marks += marks
        total_time += attempt.get("time_taken_minutes", 0)
        total_attempted += attempt.get("attempted", 0)

    # Calculate Strengths and Weaknesses
    sorted_chapters = sorted(chapter_stats.items(), key=lambda x: (x[1]["marks"]/x[1]["attempts"]), reverse=True)
    strengths = [ch[0] for ch in sorted_chapters[:2]] if sorted_chapters else []
    weaknesses = [ch[0] for ch in sorted_chapters[-2:]] if sorted_chapters else []

    return {
        "student_id": student_id,
        "name": student.get("name"),
        "metrics": {
            "total_marks_across_sessions": total_marks,
            "total_time_spent_mins": total_time,
            "total_questions_attempted": total_attempted
        },
        "chapter_breakdown": chapter_stats,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "trends": time_series
    }

@app.post("/recommend/{student_id}")
def recommend_steps(student_id: str):
    analysis = analyze_student(student_id)
    weaknesses = analysis["weaknesses"]
    strengths = analysis["strengths"]
    
    steps = []
    
    # Step 1: Concept revision for weakest subject
    if weaknesses:
        steps.append({
            "step_number": 1,
            "dost_type": "concept",
            "target_chapter": weaknesses[0],
            "params": dost_db.get("concept", {}).get("params", {}),
            "questions": [],
            "reasoning": f"Your weakest chapter is {weaknesses[0]}. Let's revise the core theory.",
            "message": f"Hey {analysis['name']}, let's start by brushing up on {weaknesses[0]}!"
        })

    # Step 2: Practice Assignment for weaknesses
    weak_questions = [q["qid"] for q in questions_db if q.get("qid") and "PHY" in q["qid"]][:5] # simplified lookup for demo
    steps.append({
        "step_number": 2,
        "dost_type": "practiceAssignment",
        "target_chapter": weaknesses[-1] if len(weaknesses) > 1 else weaknesses[0],
        "params": dost_db.get("practiceAssignment", {}).get("params", {}),
        "questions": weak_questions,
        "reasoning": "Targeted practice on weak areas without time pressure.",
        "message": "Now let's apply what you've learned. Take your time!"
    })

    # Step 3: Speed drill on a strong topic to boost confidence
    strong_questions = [q["qid"] for q in questions_db if q.get("qid") and "MAT" in q["qid"]][:10]
    if strengths:
        steps.append({
            "step_number": 3,
            "dost_type": "clickingPower",
            "target_chapter": strengths[0],
            "params": dost_db.get("clickingPower", {}).get("params", {}),
            "questions": strong_questions,
            "reasoning": "Speed drill on a strong topic to improve overall timing and build confidence.",
            "message": "Let's test your speed! You're great at this topic."
        })

    return {
        "student_id": student_id,
        "recommendation_plan": steps
    }

@app.get("/leaderboard")
def get_leaderboard():
    scores = []
    for s in students_db:
        stu_id = s["student_id"]
        # Use our analysis endpoint logic directly
        chapter_stats = {}
        total_marks = 0
        for attempt in s.get("attempts", []):
            marks = parse_marks(attempt.get("marks", 0))
            total_marks += marks
            for ch in attempt.get("chapters", []):
                if ch not in chapter_stats:
                    chapter_stats[ch] = 0
                chapter_stats[ch] += marks
                
        sorted_chapters = sorted(chapter_stats.items(), key=lambda x: x[1], reverse=True)
        strength = sorted_chapters[0][0] if sorted_chapters else "None"
        weakness = sorted_chapters[-1][0] if sorted_chapters else "None"
        
        # Scoring logic: Marks * completion bonus
        score = total_marks * 10
        scores.append({
            "student_id": stu_id,
            "name": s["name"],
            "score": score,
            "strength": strength,
            "weakness": weakness,
            "focus_area": weakness
        })
        
    scores.sort(key=lambda x: x["score"], reverse=True)
    for i, sc in enumerate(scores):
        sc["rank"] = i + 1
        
    return {"leaderboard": scores}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
