from fastapi import APIRouter, Request
from app.modules.scrape.services import scrape_url_by_command

#prefix /scrape
router = APIRouter()

tags = "scrape"

@router.post("/", tags=[tags])
def scrape_url(url: str, req: Request):
    return scrape_url_by_command(url, req)