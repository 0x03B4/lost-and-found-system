from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

# Public pages

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "public/homepage.html")

@app.get("/search")
def search(request: Request):
    return templates.TemplateResponse(request, "public/search_page.html")

@app.get("/privacy")
def privacy(request: Request):
    return templates.TemplateResponse(request, "public/privacy_policy.html")

@app.get("/terms")
def terms(request: Request):
    return templates.TemplateResponse(request, "public/terms_of_service.html")

@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(request, "public/contact_us.html")

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request, "public/login.html")

@app.get("/reset")
def reset(request: Request):
    return templates.TemplateResponse(request, "public/reset_password.html")