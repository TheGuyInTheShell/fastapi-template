from plugins.scraper import scrape
from fastapi import Request
from typing import Optional


def scrape_url_by_command(url: str, req: Optional[Request] = None):
    return scrape.commands.execute(req, {"url": url})