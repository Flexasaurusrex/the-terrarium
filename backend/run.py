"""
THE TERRARIUM - MODE SWITCHER
Runs different scenarios based on SCENARIO_MODE env var
"""

from config import SCENARIO_MODE

print(f"🎭 Starting Terrarium in {SCENARIO_MODE.upper()} mode...")

if SCENARIO_MODE == 'legends':
    print("🎸 Loading LEGENDS NIGHT OUT scenario...")
    from legends_engine import LegendsEngine
    engine = LegendsEngine()
else:
    print("📺 Loading TRUMAN SHOW scenario...")
    from spawn_engine import TerrariumSpawnEngine
    engine = TerrariumSpawnEngine()

# Run the selected engine
engine.run()
```

---

## **STEP 3: ADD THE 3 LEGENDS FILES**

Copy the three files I gave you earlier into `backend/`:
- `legends_personas.py`
- `legends_generator.py`
- `legends_engine.py`

---

## **STEP 4: UPDATE RAILWAY DEPLOYMENT:**

### **A. Update the start command:**

In Railway:
1. Go to Settings
2. Find "Start Command" or update your `Procfile`/`railway.json`
3. Change from `python spawn_engine.py` to:
```
python run.py
