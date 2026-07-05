Full stack recommendation system

Overview

This is a FastAPI + Next.JS applications that lets registered users use this system as a news recommender, for example: sky news or BBC news

This project has been tested on the following installations:

- Python 3.12.10
- Node.js v24.18.0 (LTS)
- npm (bundled with Node.js)
- Windows 11

################################################
Step 1. Requirements Installation

1.1 Install the backend requirements
- Python 3.12.10

1.2 Install the frontend requirements
- Node.js v24.18.0 LTS 
################################################

################################################
Step 2. Setup Instructions

2.1  Install the backend packages requirements

Head into /Backend open CMD and run:

- pip install -r requirements.txt

2.2  Install the frontend package requirements

Head into /Frontend open CMD and run:

- npm install
################################################

################################################
Step 3. Run everything together

3.1 Once all the previous steps have been successfully ran and installed we can run the system

Head over to the Root directory and run:

- Start.bat

This should open 2 terminals, one for Backend and one for frontend

This will launch:

FastAPI backend
Next.js frontend

3.2 To use the API routes (barebones testing)

Head to the following link in your browser:

http://127.0.0.1:8000/docs

This provides the FastAPI Swagger UI where all backend routes can be tested manually.

To use the frontend

Head to the following link in your browser:

http://localhost:3000

################################################

PLEASE READ / CAUTIONS

- Before running the application, please ensure the following:
- Ensure Python is installed correctly (Python 3.12.10 recommended)
- Ensure Node.js is installed (LTS version recommended)
- Ensure npm is available (comes with Node.js installation)
- Run pip install -r requirements.txt before starting the backend
- Run npm install inside the /Frontend directory before starting the frontend
- Do NOT delete the node_modules folder once installed
- Ensure the backend is running before using the frontend
- If ports are already in use (8000 or 3000), close conflicting applications
- Run start.bat from the root directory only

If the application does not start correctly:

- Restart both terminals
- Re-run start.bat
- Ensure all dependencies are installed

