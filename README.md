# aai
AtomicAI API

### Setup
Create a new environment with all necessary dependencies by cloning this repo and running
`conda env update --file aai.cpu.yml`

### Connect to frontend Streamlit app locally
In the `aai` repo, type `uvicorn main:app --reload`  
This will launch the backend on your local machine.
Go to `http://localhost:8000/docs` in your browser to see the API functions and test them out.
