"""
TERRARIUM: LEGENDS NIGHT OUT
Conversation generation for the three legends
"""

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, MODEL_NAME
from legends_personas import LEGENDS, LOCATIONS, SCENARIO_TIMELINE
import random

def get_current_scenario_context(loop_time_minutes):
    """Get location and mood based on time in loop (0-360 minutes = 6 hours)"""
    hour = loop_time_minutes // 60
    
    # Find appropriate scenario event
    time_hour = 22 + hour  # Start at 10 PM (22:00)
    if time_hour >= 24:
        time_hour -= 24
    
    # Find closest scenario event
    for i, event in enumerate(SCENARIO_TIMELINE):
        event_time = int(event['time'].split(':')[0])
        if event_time >= 12:  # PM times
            event_hour = event_time
        else:  # AM times
            event_hour = event_time
            
        if abs(event_hour - time_hour) <= 1:
            return event
    
    return SCENARIO_TIMELINE[0]  # Default to first event

def generate_legend_comment(
    speaker_id,
    loop_time_minutes,
    loop_number,
    target_speaker_id,
    target_comment,
    conversation_history=""
):
    """Generate a comment from one legend to another"""
    
    speaker = LEGENDS[speaker_id]
    target = LEGENDS[target_speaker_id]
    scenario = get_current_scenario_context(loop_time_minutes)
    location = LOCATIONS[scenario['location']]
    mood = scenario['mood']
    
    # Build context
    time_display = f"{22 + (loop_time_minutes // 60)}:00" if loop_time_minutes < 120 else f"{(loop_time_minutes // 60) - 2}:00 AM"
    
    prompt = f"""You are {speaker['human_name']} in Greenwich Village, NYC, 1969.

CURRENT SITUATION:
- Time: {time_display}
- Location: {location['name']} - {location['description']}
- Vibe: {location['vibe']}
- Your mood: {speaker['mood_states'][mood]}
- You're drinking: {speaker['drink']}
- Loop #{loop_number} (you DO NOT remember previous loops)

YOUR PERSONALITY:
{speaker['personality']}

SPEAKING STYLE:
{speaker['speaking_style']}

{target['human_name']} just said to you:
"{target_comment}"

{f"Recent conversation context: {conversation_history}" if conversation_history else ""}

CRITICAL RULES:
- Stay completely in character as {speaker['human_name']}
- Respond naturally to what they said
- Match the mood and location vibe
- Keep it conversational, like you're in a bar/park/diner
- 1-3 sentences maximum
- NO asterisks or actions
- Sound like YOU, not like generic AI

Respond as {speaker['human_name']}:"""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=200,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text.strip()

def generate_legend_intro(speaker_id, loop_time_minutes, loop_number):
    """Generate an opening statement from a legend"""
    
    speaker = LEGENDS[speaker_id]
    scenario = get_current_scenario_context(loop_time_minutes)
    location = LOCATIONS[scenario['location']]
    mood = scenario['mood']
    
    time_display = "10:00 PM" if loop_time_minutes < 60 else f"{10 + (loop_time_minutes // 60)}:00 PM"
    
    prompt = f"""You are {speaker['human_name']} in Greenwich Village, NYC, 1969.

CURRENT SITUATION:
- Time: {time_display}
- Location: {location['name']} - {location['description']}
- Event: {scenario['event']}
- Your mood: {speaker['mood_states'][mood]}
- You're drinking: {speaker['drink']}
- Loop #{loop_number}

YOUR PERSONALITY:
{speaker['personality']}

SPEAKING STYLE:
{speaker['speaking_style']}

This is your opening statement as you arrive/sit down. Make an observation or say something in character.

CRITICAL RULES:
- Stay completely in character
- React to the location/situation
- 1-2 sentences
- NO asterisks or actions
- Sound like YOU

{speaker['human_name']} says:"""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=150,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text.strip()
