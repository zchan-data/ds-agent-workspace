# Playbook: REST API Deployment

## Stack

- **Framework**: FastAPI
- **Server**: Uvicorn (dev), Gunicorn + Uvicorn workers (prod)
- **Validation**: Pydantic models for request/response schemas
- **Containerization**: Docker (recommended even for local dev)

## Checklist

- [ ] Define Pydantic `RequestModel` and `ResponseModel` matching training feature schema
- [ ] Load model artifact at startup using `@app.on_event("startup")` (or lifespan context)
- [ ] Apply the same preprocessing pipeline used at training time (load the serialized Pipeline)
- [ ] Add `/health` endpoint returning 200 + version info
- [ ] Add input validation with meaningful error messages (422 on bad input)
- [ ] Log each request: input hash, prediction, latency, timestamp
- [ ] Write at least one integration test that POSTs a sample input and checks the response
- [ ] Pin all dependencies in `requirements.txt`

## Project Structure

```
app/
├── main.py          ← FastAPI app, routes
├── models.py        ← Pydantic schemas
├── predictor.py     ← model loading and inference logic
├── Dockerfile
└── requirements.txt
```

## Notes

<!-- Add project-specific notes here -->
