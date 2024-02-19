import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.password_controller import router

# from src.middleware.auth_middleware import check_token_status

app = FastAPI(title="Password Manager", version='1.0.0' ,description='')

app.include_router(router)

# app.middleware("http")(check_token_status)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
