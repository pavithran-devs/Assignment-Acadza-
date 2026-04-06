import os
import json
from main import app, analyze_student, recommend_steps, get_leaderboard, students_db

def generate_all():
    os.makedirs("sample_outputs", exist_ok=True)
    
    # Generate Leaderboard
    lb = get_leaderboard()
    with open("sample_outputs/leaderboard.json", "w") as f:
        json.dump(lb, f, indent=2)
        
    for student in students_db:
        sid = student["student_id"]
        
        analysis = analyze_student(sid)
        recs = recommend_steps(sid)
        
        output = {
            "analysis": analysis,
            "recommendations": recs
        }
        
        with open(f"sample_outputs/{sid}_output.json", "w") as f:
            json.dump(output, f, indent=2)

    print("Successfully generated all sample outputs!")

if __name__ == "__main__":
    generate_all()
