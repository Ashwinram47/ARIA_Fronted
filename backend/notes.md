1. Seperate frontend/backend connected with FastAPI
- CORSMiddleware 

2. Document submission
- `UploadFile` with `python-multipart` installed, accept `List[UploadFile]` on a POST endpoint
- Just filename classification for now

3. AI Layer
- Input asset dictionary (`{"tag": "P-101", "pid": True, "datasheet": False, ...}`) to get explanation of 1. whats missing (reason) and 2. whos responsible (action)
- Just use a hosted API, Anthropic or Google Vertex AI Developer acc for free tokens