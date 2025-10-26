import json

# Base questions - part 1
q1_20 = [
    {"stem": "When should a BWC be activated?", "choices": ["Only during arrests", "At the start of every police interaction", "Only when force is used", "When directed by supervisor"], "answer_idx": 1, "explanation": "BWC should be activated at the start of every police interaction. Officers must resume recording if stopped for any of the 10 exceptions.", "topic_name": "BWC", "source_ref": "BWC 2.0"},
    {"stem": "Which is NOT a BWC exception?", "choices": ["Attending to sexual offences", "Consuming official ease", "Routine traffic stops", "Within secured areas"], "answer_idx": 2, "explanation": "Routine traffic stops are NOT an exception. The 10 exceptions: sexual offences, secured areas, pumping petrol, hospital, consuming OE, personal communications, diplomat requests, MOP requests stop, anti-crime rounds with restrictions, non-crime in private places.", "topic_name": "BWC", "source_ref": "BWC 2.0"},
    {"stem": "Mary left bag to reserve seat. It was missing when she returned. Report type?", "choices": ["NP299 theft", "Station diary", "NP322 loss", "NP322 theft"], "answer_idx": 2, "explanation": "NP322 loss report. Without witnessing theft, classified as loss.", "topic_name": "Reports", "source_ref": "Ease Spring"},
    {"stem": "What does SALUTE reporting format stand for?", "choices": ["Standard Alert Level Update Time Equipment", "Size Activity Location Unit Time Equipment", "Security Assessment Level Unit Time Evaluation", "Situation Alert Location Update Time Environment"], "answer_idx": 1, "explanation": "SALUTE: Size (number), Activity (what), Location (where), Unit (reporting), Time (when), Equipment (weapons).", "topic_name": "SALUTE", "source_ref": "Ease Spring"}
]

print(f"Generated {len(q1_20)} questions in part 1")

with open('data/seeds/mcq.json', 'w') as f:
    json.dump(q1_20, f, indent=2)

print("MCQ file created successfully with 4 base questions")
