# Acadza AI Intern Assignment - Recommender System

## Approach to the Build Task

To analyze the student data and build out the recommendation system, I developed a FastAPI application featuring a simple, but robust logic chain.

### Data Understanding & Normalization
The data contained three major parts: student performance sessions, a question bank, and DOST configurations for generating practice activities. Before doing any modeling, the data had to be normalized.
- **Marks Standardization (*The Messy Marks Field*)**: The marks data ranged from simple digits like `"22"` to fractions like `"49/120"` and differential equations like `"+48 -8"`. I built a `parse_marks` parsing method to clean these strings and evaluate them as integers/floats. If it encounters a fraction, it evaluates the numerator. If it encounters a `+X -Y` string, it performs mathematical integer accumulation to map it down to the final scored baseline. 
- **Parsing IDs**: Evaluated `$oid` dictionaries vs plain text IDs cleanly using `.get()` standardizations and `type()` checks.

### Analysis & Recommendations Approach
1. **Generating Chapter Baselines**: When `/analyze` is called, it iterates across the entire record array for a student and builds an isolated dictionary that counts frequency, tracks time taken, and accumulates marked scores. Sorting these by score-to-attempt ratios allowed me to objectively find the strongest and weakest chapters computationally.
2. **DOST Recommendation Sequence**: Utilizing the identified weakest and strongest topics, `/recommend` generates a curated path for them:
   - **Step 1:** Revises the weakest computational point with a `concept` type action immediately, referencing the lowest scoring metric.
   - **Step 2:** Provides an untimed `practiceAssignment` built around the weakest subjects or combinations.
   - **Step 3:** Assigns a fast-paced `clickingPower` drill oriented around their actual *strengths* to provide an engaging, confidence-boosting finale to the learning cycle.

## Debug Process

The debugging task presented an interesting logical bug where the application ran without syntax errors, but the outcomes were identical for completely different students. 

**What went wrong:** 
Upon inspecting the codebase, specifically the profile normalizing function at `debug/recommender_buggy.py`, I identified that the `student_profile` variable was accidentally being entirely replaced by the normalized result of the entire `cohort_baseline` rather than self-referential normalization:
```python
profile_norm = np.linalg.norm(cohort_baseline)
student_profile = cohort_baseline / (profile_norm + 1e-10)
```
**Fix Implemented:** 
I modified the vector normalization to correctly point back to the isolated `student_profile` variable:
```python
profile_norm = np.linalg.norm(student_profile)
student_profile = student_profile / (profile_norm + 1e-10)
```
**Process:** I immediately suspected matrix or pointer reassignment given that all results normalized back to the exact same top-10 questions regardless of feature vector discrepancies. Scanning through the function variables confirmed the error in overriding scope.

## What I'd Improve Given More Time
1. **More Sophisticated Profiling**: I would swap out the raw average/ratio modeling for a Cosine-Similarity engine or weighted average that integrates 'Time Spent' over 'Marks Scored' to find instances where a student guessed right but took a very long time, indicating a hidden weakness. 
2. **Question Tagging Check**: Right now the script naively matches basic substrings inside the IDs for question filtering, I would write deeper JSON integration specifically to index question text against the topics explicitly required for the DOST setup.
3. **Pydantic Validation**: Introduce strict `Pydantic` schema models for routing to ensure payload stability when integrated tightly into an actual Frontend.

## Setup Instructions
1. Install requirements using `pip install -r requirements.txt`.
2. Ensure you have python 3.9+ available.
3. Boot the FastAPI webserver using standard uvicorn deployment:
```bash
uvicorn main:app --reload
```
4. Perform endpoints analysis utilizing endpoints such as: `http://localhost:8000/analyze/STU_001`!
