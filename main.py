"""
This project is now structured as:

- backend/  → FastAPI server exposing the simulation
- frontend/ → React UI for visualization and control
- aiml/, ui/, utils.py, config.py → your original simulation logic (unchanged)

To run:
1. Start backend: uvicorn backend.main:app --reload
2. Start frontend: npm start (inside frontend/)
"""

print("This project now uses FastAPI backend + React frontend.")
print("Run the backend server using:")
print("  uvicorn backend.main:app --reload")
