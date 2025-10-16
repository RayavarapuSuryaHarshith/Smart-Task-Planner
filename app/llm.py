import os
import asyncio
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.INFO)

# Load local .env if present for developer convenience
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Get API key dynamically to support runtime updates
def get_groq_key():
    # Read Groq API key from environment variable
    return os.getenv("GROQ_API_KEY")


class Task(BaseModel):
    title: str
    description: str = ""
    duration_days: int
    start_day: int
    end_day: int
    depends_on: List[str] = []
    priority: str = "medium"
    phase: str = "development"


async def call_groq(prompt: str) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=get_groq_key())
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert project manager. Create realistic, actionable task breakdowns with proper dependencies and timelines. Always return valid JSON arrays of tasks."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        raise


def analyze_goal_type(goal: str) -> str:
    """Analyze goal to determine project type for better planning"""
    goal_lower = goal.lower()

    # use simple word-boundary checks to avoid accidental matches
    import re
    def has(words):
        for w in words:
            if re.search(r"\b" + re.escape(w) + r"\b", goal_lower):
                return True
        return False

    if has(['exam', 'test', 'study', 'course', 'learn', 'prepare', 'prepare for']):
        return 'study'
    elif has(['trip', 'travel', 'vacation', 'holiday', 'journey', 'visit', 'book flight', 'itinerary']):
        return 'travel'
    elif has(['wedding', 'party', 'celebration', 'birthday', 'anniversary']):
        return 'event'
    elif has(['job', 'interview', 'career', 'resume', 'application', 'cv']):
        return 'career'
    elif has(['fitness', 'workout', 'exercise', 'gym', 'health', 'weight', 'fit', 'get fit', 'lose weight', 'gain muscle', 'training']):
        return 'fitness'
    elif has(['house', 'move', 'relocate', 'apartment', 'home']):
        return 'housing'
    elif has(['cook', 'recipe', 'meal', 'dinner', 'food', 'bake']):
        return 'cooking'
    elif has(['app', 'software', 'website', 'platform', 'system', 'code']):
        return 'software'
    elif has(['product', 'launch', 'business', 'startup']):
        return 'product'
    elif has(['marketing', 'campaign', 'promotion', 'brand', 'advertise']):
        return 'marketing'
    else:
        return 'general'

def fallback_plan(goal: str, due_days: int | None) -> List[Dict[str, Any]]:
    """Intelligent fallback planning based on goal analysis with domain-specific tasks"""
    if not due_days:
        due_days = 14
    
    goal_lower = goal.lower()
    tasks: List[Dict[str, Any]] = []
    
    # Define goal-specific task templates
    if any(word in goal_lower for word in ['exam', 'test', 'study', 'course', 'learn']):
        # Detect explicit subject list like 'subjects like maths, physics, chemistry'
        import re
        subjects = []
        m = re.search(r"subjects?\s*(?:like|:)?\s*(.+)$", goal_lower)
        if m:
            # split by comma or 'and'
            raw = m.group(1)
            # remove trailing punctuation
            raw = re.sub(r"[.\\n]$", "", raw).strip()
            parts = re.split(r",| and | & ", raw)
            subjects = [p.strip() for p in parts if p.strip()]

        # If subjects found, create per-subject study tasks
        if subjects:
            # allocate days: reserve 1-2 days for mock tests/final depending on due_days
            reserved = max(1, due_days // 6)
            study_days = max(1, due_days - reserved)
            per_subj = max(1, study_days // len(subjects))

            phases = []
            phases.append(("Create Study Schedule", 1, "Plan study timeline, allocate time for each subject/topic"))
            phases.append(("Gather Study Materials", 1, "Collect textbooks, notes, practice tests, online resources"))
            # For each subject, add Read and Practice tasks
            for subj in subjects:
                title_read = f"Read & Review {subj.title()}"
                title_practice = f"Practice Problems - {subj.title()}"
                # give each subject a read + practice block
                phases.append((title_read, max(1, per_subj // 2), f"Read notes and textbooks for {subj.strip()}"))
                phases.append((title_practice, max(1, per_subj - (per_subj // 2)), f"Solve practice problems for {subj.strip()}") )

            phases.append(("Mock Tests", reserved, "Take practice exams, identify weak areas, time yourself"))
            phases.append(("Final Review", 1, "Quick revision, review mistakes, boost confidence"))
        else:
            phases = [
                ("Create Study Schedule", max(1, due_days // 10), "Plan study timeline, allocate time for each subject/topic"),
                ("Gather Study Materials", max(1, due_days // 8), "Collect textbooks, notes, practice tests, online resources"),
                ("Review and Read", max(2, due_days // 3), "Read through materials, take detailed notes, highlight key concepts"),
                ("Practice and Write", max(2, due_days // 3), "Solve practice problems, write summaries, create flashcards"),
                ("Mock Tests", max(1, due_days // 6), "Take practice exams, identify weak areas, time yourself"),
                ("Final Review", max(1, due_days // 8), "Quick revision, review mistakes, boost confidence")
            ]
    elif any(word in goal_lower for word in ['trip', 'travel', 'vacation', 'holiday', 'journey']):
        phases = [
            ("Plan Itinerary", max(1, due_days // 6), "Research destinations, create day-by-day schedule"),
            ("Book Transportation", max(1, due_days // 8), "Book flights, trains, rental cars, local transport"),
            ("Book Accommodation", max(1, due_days // 8), "Reserve hotels, hostels, Airbnb, check-in details"),
            ("Prepare Documents", max(1, due_days // 10), "Check passport, visas, travel insurance, tickets"),
            ("Pack Essentials", max(1, due_days // 6), "Pack clothes, toiletries, electronics, medications"),
            ("Final Preparations", max(1, due_days // 10), "Confirm bookings, download maps, notify bank, charge devices")
        ]
    elif any(word in goal_lower for word in ['wedding', 'party', 'celebration', 'birthday']):
        phases = [
            ("Set Budget and Guest List", max(1, due_days // 6), "Determine budget, create guest list, send save-the-dates"),
            ("Book Venue and Vendors", max(2, due_days // 4), "Reserve venue, book catering, photographer, DJ/band"),
            ("Plan Details", max(1, due_days // 4), "Choose decorations, menu, flowers, entertainment"),
            ("Send Invitations", max(1, due_days // 8), "Design and send invitations, track RSVPs"),
            ("Final Arrangements", max(1, due_days // 6), "Confirm all vendors, prepare timeline, delegate tasks"),
            ("Day-of Execution", 1, "Set up decorations, coordinate vendors, enjoy the celebration")
        ]
    elif any(word in goal_lower for word in ['job', 'interview', 'career', 'resume']):
        phases = [
            ("Update Resume", max(1, due_days // 6), "Revise resume, highlight relevant experience and skills"),
            ("Research Companies", max(1, due_days // 5), "Identify target companies, research their culture and requirements"),
            ("Apply for Positions", max(2, due_days // 4), "Submit applications, write cover letters, follow up"),
            ("Prepare for Interviews", max(1, due_days // 4), "Practice common questions, research interviewers, plan outfits"),
            ("Mock Interviews", max(1, due_days // 8), "Practice with friends, record yourself, refine answers"),
            ("Follow Up", max(1, due_days // 10), "Send thank you emails, follow up on applications")
        ]
    elif any(word in goal_lower for word in ['fitness', 'workout', 'exercise', 'gym', 'health']):
        phases = [
            ("Set Fitness Goals", max(1, due_days // 8), "Define specific targets: weight, strength, endurance"),
            ("Create Exercise Plan", max(1, due_days // 6), "Design workout schedule, choose exercises, plan rest days"),
            ("Start Light Workouts", max(2, due_days // 4), "Begin with basic exercises, focus on form over intensity"),
            ("Increase Intensity", max(2, due_days // 3), "Add more weight, longer sessions, challenging exercises"),
            ("Track Progress", max(1, due_days // 6), "Monitor improvements, adjust plan, celebrate milestones"),
            ("Maintain Routine", max(1, due_days // 8), "Establish sustainable habits, plan for long-term success")
        ]
    elif any(word in goal_lower for word in ['house', 'move', 'relocate', 'apartment']):
        phases = [
            ("Research Locations", max(1, due_days // 6), "Find neighborhoods, check schools, amenities, commute"),
            ("Search Properties", max(2, due_days // 4), "Browse listings, schedule viewings, compare options"),
            ("Secure Financing", max(1, due_days // 6), "Get mortgage pre-approval, gather financial documents"),
            ("Make Offer", max(1, due_days // 8), "Submit offers, negotiate terms, arrange inspections"),
            ("Finalize Purchase", max(1, due_days // 6), "Complete paperwork, arrange insurance, schedule closing"),
            ("Plan Move", max(1, due_days // 8), "Book movers, pack belongings, change address")
        ]
    elif any(word in goal_lower for word in ['cook', 'recipe', 'meal', 'dinner', 'food']):
        phases = [
            ("Choose Recipes", max(1, due_days // 8), "Select dishes, consider dietary restrictions, difficulty level"),
            ("Plan Menu", max(1, due_days // 10), "Create meal schedule, balance nutrition, estimate portions"),
            ("Shop for Ingredients", max(1, due_days // 6), "Make shopping list, visit grocery stores, buy fresh ingredients"),
            ("Prep Ingredients", max(1, due_days // 4), "Wash, chop, marinate ingredients, organize workspace"),
            ("Cook and Practice", max(2, due_days // 3), "Follow recipes, practice techniques, taste and adjust"),
            ("Serve and Present", max(1, due_days // 8), "Plate food beautifully, set table, enjoy the meal")
        ]
    else:  # Generic goal
        phases = [
            ("Research and Plan", max(1, due_days // 5), "Understand requirements, research options, create action plan"),
            ("Gather Resources", max(1, due_days // 6), "Collect necessary materials, tools, information, contacts"),
            ("Start Implementation", max(2, due_days // 3), "Begin working on main tasks, focus on key activities"),
            ("Review and Refine", max(1, due_days // 6), "Check progress, make improvements, address issues"),
            ("Finalize and Complete", max(1, due_days // 8), "Complete remaining tasks, do final checks"),
            ("Wrap Up", max(1, due_days // 10), "Finish up, document results, celebrate achievement")
        ]
    
    day_cursor = 0
    for i, (phase_name, length, description) in enumerate(phases):
        # Ensure we don't exceed the deadline
        remaining_days = due_days - day_cursor
        if remaining_days <= 0:
            break
            
        # Adjust length if we're running out of days
        actual_length = min(length, max(1, remaining_days - (len(phases) - i - 1)))
        
        task = {
            "title": f"{phase_name}",
            "description": description,
            "duration_days": actual_length,
            "start_day": day_cursor,
            "end_day": day_cursor + actual_length,
            "depends_on": [tasks[-1]["title"]] if tasks else [],
            "phase": phase_name.lower().replace(" ", "_"),
            "priority": "high" if i < 2 else "medium"
        }
        tasks.append(task)
        day_cursor += actual_length
    
    return tasks


def _extract_json_array(text: str):
    import re, json
    m = re.search(r"(\[\s*\{.*\}\s*\])", text, re.S)
    if m:
        jtxt = m.group(1)
        try:
            return json.loads(jtxt)
        except Exception:
            return None
    try:
        return json.loads(text)
    except Exception:
        return None


async def generate_plan(goal: str, due_days: int | None = None):
    logging.info(f"generate_plan called: goal={goal!r} due_days={due_days}")
    
    if not due_days:
        due_days = 14
    
    # Enhanced prompt for goal-specific planning
    prompt = f"""
As an expert life/project planner, create a realistic, domain-specific task breakdown for this goal:

**Goal**: {goal}
**Timeline**: {due_days} days
**Today**: Day 0

CRITICAL: Use tasks and terminology that are SPECIFIC to this goal's domain. 

Examples of domain-specific tasks:
- For studying/exams: "Read chapters 1-3", "Practice math problems", "Create flashcards", "Take mock test"
- For travel: "Book flights", "Pack suitcase", "Get travel insurance", "Download offline maps"  
- For fitness: "Do cardio workout", "Practice yoga", "Track calories", "Weigh yourself"
- For cooking: "Shop for ingredients", "Prep vegetables", "Marinate meat", "Set the table"
- For job search: "Update LinkedIn", "Practice interview questions", "Research companies", "Send follow-up emails"

Avoid generic terms like "design", "develop", "test", "launch" unless the goal is actually about software/product development.

Return ONLY a valid JSON array of tasks with this exact structure:
[
  {{
    "title": "Specific, actionable task using domain terminology",
    "description": "Clear explanation of what to do and why",
    "duration_days": 2,
    "start_day": 0,
    "end_day": 2,
    "depends_on": ["Previous task title"],
    "priority": "high|medium|low",
    "phase": "preparation|action|completion"
  }}
]

Requirements:
- Use vocabulary and tasks specific to the goal's domain
- Start with day 0, end by day {due_days}
- Each task should be 1-{max(1, due_days//3)} days duration
- Make tasks concrete and actionable (not abstract phases)
- Include realistic time buffers
- Use appropriate phase names (not generic "development/testing")
"""

    openai_key = get_groq_key()
    if openai_key:
        logging.info("GROQ_API_KEY found, calling Groq with enhanced prompt")
        try:
            text = await call_groq(prompt)
            arr = _extract_json_array(text)
            
            if arr is None:
                logging.warning("Groq returned non-JSON, using intelligent fallback")
                return fallback_plan(goal, due_days)

            # Enhanced validation with fallback fields
            validated = []
            for item in arr:
                try:
                    # Ensure required fields exist with defaults
                    task_data = {
                        "title": item.get("title", "Unnamed Task"),
                        "description": item.get("description", ""),
                        "duration_days": max(1, item.get("duration_days", 1)),
                        "start_day": max(0, item.get("start_day", 0)),
                        "end_day": item.get("end_day", item.get("start_day", 0) + item.get("duration_days", 1)),
                        "depends_on": item.get("depends_on", []),
                        "priority": item.get("priority", "medium"),
                        "phase": item.get("phase", "development")
                    }
                    
                    # Validate against Task model (with relaxed validation)
                    validated.append(task_data)
                    
                except Exception as validation_error:
                    logging.warning(f"Task validation failed: {validation_error}, skipping task")
                    continue
            
            if validated:
                logging.info(f"Groq plan validated successfully: {len(validated)} tasks")
                return validated
            else:
                logging.warning("No valid tasks from Groq, using fallback")
                return fallback_plan(goal, due_days)
                
        except Exception as e:
            logging.exception("Groq call failed, using intelligent fallback")
            return fallback_plan(goal, due_days)
    else:
        logging.info("No GROQ_API_KEY, using intelligent fallback_plan")
        return fallback_plan(goal, due_days)
