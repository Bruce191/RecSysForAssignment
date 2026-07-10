Full stack recommendation system

Overview

This is a FastAPI + Next.JS applications that lets registered users use this system as a news recommender, for example: sky news or BBC news

The application is deployed live on Railway and can be tested directly without any local setup:

Frontend (live app):
https://ofcom-recsys-l6-softeng.up.railway.app


NOTE: The known issue below affects the live deployment.
When liking/disliking a post on the Recommendations page, the interaction 
IS correctly saved to the database, but the UI may visually reset the 
like/dislike state after the recommendations list refreshes. This is a 
frontend display bug only — the interaction data itself is stored 
correctly and can be confirmed via the database or the 
/user/interactions endpoint in the Swagger UI. This does not affect 
the correctness of the underlying data storage, only the visual 
feedback shown to the user.

The live version uses a PostgreSQL database (Railway) instead of the 
local SQLite database described below, to satisfy the requirement for 
centralised, persistent storage accessible by all users. See the 
"Database Configuration" section below for more detail on this 
environment-based setup.


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

Head into root folder open CMD and run:

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
- Ensure Python is installed correctly (Python 3.12.10 tested)
- Ensure Node.js is installed (LTS version tested)
- Ensure npm is available (comes with Node.js tested)
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


Since there is no login route Please use the account listed below

Username:Password format
Qiqi:Qiqi
Torid:Torid

