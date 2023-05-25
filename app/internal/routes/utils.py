from fastapi import APIRouter

router = APIRouter(
    prefix='/status'
)


# healthcheck
@router.get("/")
async def root():
    return {"message": "Hello World"}
