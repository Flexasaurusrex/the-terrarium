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

engine.run()
