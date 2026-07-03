
## local commands ###

#!/bin/bash

# Navigate to backend and start FastAPI
#cd backend
#uvicorn main:app --reload --port 8000 &

# Go back to root and navigate to frontend
cd ../frontend
npm run dev

## local commands ###


## prod commands ###

#!/bin/bash
#gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

## prod commands ###

