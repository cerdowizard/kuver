import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import models
from controllers.admin import admin
from controllers.admin.admin import admin_router
from controllers.auth.auth import router
from controllers.user.user import user_router
from database.database import engine
from controllers.transaction.transactions import transac_router
app = FastAPI(
    docs_url="/docs",
    redoc_url="/redocs",
    title="KUVER_TEC",
    description="KUVER_TEC BACKEND API",
    version="0.10",
    openapi_url="/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def create_tables():  # new
    models.Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup():
    create_tables()
    print("creating tables and starting app up")


@app.on_event("shutdown")
async def shutdown():
    print("app shutdown")


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


@app.get('/api/healthchecker')
def root():
    return {'message': 'Welcome To  KUVER_TEC Api'}


# app.include_router(auth_router.router, tags=["Auth"])
app.include_router(router, tags=["Authentication"])
app.include_router(user_router, tags=["User Account"])
app.include_router(transac_router, tags=["Transaction Actions"])
app.include_router(admin_router, tags=["Admin Actions"])
# app.include_router(adminRoute, tags=["Admin Action"])
# app.include_router(user_router, tags=["User"])
# app.include_router(post_router, tags=["Post"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port="1997")
