# init_everything.py
import os
from database import init_db, seed_motivations, seed_achievements

print("🔧 Setting up...")
init_db()
seed_motivations()
seed_achievements()

# Create folders
os.makedirs('static', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)

print("✅ DONE! Now run: python app.py")