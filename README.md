# Procare
An online health management solution for the workplace

## Platform Installation
**Required dependencies:**
- Python 3

**Installation Instructions:**
1. Clone the repository
2. Change directory to the repository (`cd procare` by default)
3. Create a virtual environment (`python3 -m venv venv`)
4. Activate virtual environment (`. venv/bin/activate`)
5. Install dependencies (`pip install -r requirements.txt`)

**Startup Instructions**
1. Change directory to the repository (`cd procare` by default)
2. Activate virtual environment (`. venv/bin/activate`)
3. Run flask (`flask run`)
4. Visit locally: http://127.0.0.1:5000/
5. `CTRL + C` to exit

**Updating dependencies**
If you have updated dependencies (e.g. imported a new library):
1. Freeze changes `pip freeze > requirements.txt`
2. Push the changes to `requirements.txt` to git
