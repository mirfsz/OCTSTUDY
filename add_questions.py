import json

# Read existing questions
with open('data/seeds/mcq.json', 'r') as f:
    existing = json.load(f)

# Additional questions to add (continuing from the user's list)
additional_questions = [
    {
        "stem": "Officer enters wrong unit for call. What action?",
        "choices": ["Apologise and leave, report SD", "Ignore", "Pretend correct", "Blame resident"],
        "answer_idx": 0,
        "explanation": "Apologise and leave, report SD. Trap: Not documenting mistake. One-liner: Own error? Record clear.",
        "topic_name": "Administrative",
        "source_ref": "User Input"
    },
    {
        "stem": "Counter complainant aggressive. What action?",
        "choices": ["Shout back", "Calm tone, call TL if continues", "Ask to leave immediately", "Switch off BWC"],
        "answer_idx": 1,
        "explanation": "Calm tone, call TL if continues. Trap: Raising voice escalates. One-liner: Stay calm, call TL.",
        "topic_name": "Counter Duties",
        "source_ref": "User Input"
    },
    {
        "stem": "Borrowed vehicle unreturned. What offence?",
        "choices": ["Theft s378 PC", "Criminal breach of trust s405 PC", "Misappropriation s403 PC", "Civil matter"],
        "answer_idx": 1,
        "explanation": "Criminal breach of trust s405 PC. Trap: Marking as theft; property lawfully obtained first. One-liner: Given then kept = CBT.",
        "topic_name": "Theft",
        "source_ref": "User Input"
    },
    {
        "stem": "Senior citizen found wandering confused. What action?",
        "choices": ["Ignore unless crime", "Bring to NPC, inform POCC and MSF", "Call family only", "Refer to hospital directly"],
        "answer_idx": 1,
        "explanation": "Bring to NPC, inform POCC and MSF. Trap: Thinking no report needed. One-liner: Lost elder = Police + MSF.",
        "topic_name": "Missing Person",
        "source_ref": "User Input"
    },
    {
        "stem": "Found firearm cartridge on ground. What action?",
        "choices": ["Pick up barehanded", "Cordon, inform TL/ARMS, await SOCO", "Keep as souvenir", "Dispose safely"],
        "answer_idx": 1,
        "explanation": "Cordon, inform TL/ARMS, await SOCO. Trap: Moving exhibit before SOCO. One-liner: Bullet seen = Scene lock.",
        "topic_name": "Arms & Explosives",
        "source_ref": "User Input"
    },
    {
        "stem": "Youth spray-paints lift wall. What offence?",
        "choices": ["Mischief", "Vandalism Act 1966 - arrestable", "Public nuisance", "Civil damage"],
        "answer_idx": 1,
        "explanation": "Vandalism Act 1966 - arrestable. Trap: Calling it Mischief (lesser offence). One-liner: Spray = Vandal, not Mischief.",
        "topic_name": "Vandalism",
        "source_ref": "User Input"
    },
    {
        "stem": "Neighbour video-records dispute. What action?",
        "choices": ["Confiscate phone", "Allow if non-interfering", "Delete footage", "Arrest for filming"],
        "answer_idx": 1,
        "explanation": "Allow if non-interfering. Trap: Forcing deletion. One-liner: Film okay till it blocks way.",
        "topic_name": "Public Relations",
        "source_ref": "User Input"
    },
    {
        "stem": "Public asks to accompany officer into scene. What action?",
        "choices": ["Allow for transparency", "Refuse - scene control only police", "Allow with consent", "Ignore"],
        "answer_idx": 1,
        "explanation": "Refuse - scene control only police. Trap: Letting civilians into restricted scene. One-liner: Scene = Police only.",
        "topic_name": "Crime Scene",
        "source_ref": "User Input"
    },
    {
        "stem": "Officer witnesses colleague accept bribe. What action?",
        "choices": ["Confront privately only", "Report through supervisor / IAD", "Ignore", "Record video secretly"],
        "answer_idx": 1,
        "explanation": "Report through supervisor / IAD. Trap: Handling alone; must follow official channel. One-liner: See bribe = report inside.",
        "topic_name": "PGO",
        "source_ref": "User Input"
    },
    {
        "stem": "Youth posting threat online ('I'll bomb school'). What action?",
        "choices": ["Ignore, just joke", "Investigate under Terrorism or Harassment Act", "Warn online", "Refer to school only"],
        "answer_idx": 1,
        "explanation": "Investigate under Terrorism or Harassment Act. Trap: Dismissing as joke. One-liner: Online threat = real treat.",
        "topic_name": "Security Threats",
        "source_ref": "User Input"
    },
    {
        "stem": "Officer loses exhibit on way to NPC. What action?",
        "choices": ["Replace quietly", "Inform TL and record SD immediately", "Ignore if minor", "Continue patrol"],
        "answer_idx": 1,
        "explanation": "Inform TL and record SD immediately. Trap: Hiding mistake. One-liner: Lost item = Log instant.",
        "topic_name": "Evidence",
        "source_ref": "User Input"
    },
    {
        "stem": "Officer records suspect without starting BWC. What action?",
        "choices": ["Use phone camera", "Stop and activate BWC; note reason", "Continue recording with phone only", "Ignore policy"],
        "answer_idx": 1,
        "explanation": "Stop and activate BWC; note reason. Trap: Using personal phone video. One-liner: Use BWC or note why.",
        "topic_name": "BWC",
        "source_ref": "User Input"
    },
    {
        "stem": "Person reports seeing abusive graffiti 'O$P$ #02-44'. What offence?",
        "choices": ["Mischief", "UML Harassment s47 MLA", "Public nuisance", "Vandalism"],
        "answer_idx": 1,
        "explanation": "UML Harassment s47 MLA. Trap: Treating as Vandalism only. One-liner: O$P$ = UML for sure.",
        "topic_name": "UML",
        "source_ref": "User Input"
    },
    {
        "stem": "Victim scammed through romance chat. What offence?",
        "choices": ["Civil matter", "Cheating s420 PC", "Cyber harassment", "Unauthorised access"],
        "answer_idx": 1,
        "explanation": "Cheating s420 PC. Trap: Calling it relationship issue. One-liner: Love + Money = 420.",
        "topic_name": "Scams",
        "source_ref": "User Input"
    }
]

# Combine questions
all_questions = existing + additional_questions

# Write back
with open('data/seeds/mcq.json', 'w') as f:
    json.dump(all_questions, f, indent=2)

print(f"Successfully added {len(additional_questions)} questions. Total: {len(all_questions)} questions")
