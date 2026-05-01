from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import pugsql
from dotenv import load_dotenv
import os
import math
import re

app = FastAPI()

load_dotenv()

templates = Jinja2Templates(directory="src/templates")

queries = pugsql.module('src/sql/queries/')

supabase_connection = os.getenv("SUPABASE_CONNECTION_STRING")
queries.connect(supabase_connection)

# Public page
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "public/homepage.html")

@app.get("/search")
def search(request: Request):

    query_search_text = request.query_params.get("search_text")
    query_search_text = query_search_text.strip() if query_search_text is not None else query_search_text
    query_search_text = f"%{query_search_text}%" if query_search_text != "" and query_search_text is not None else query_search_text

    query_sort = request.query_params.get("sort")
    query_campuses = request.query_params.getlist("campuses")
    query_categories = [int(category_id) for category_id in request.query_params.getlist("categories")]

    query_page_number = request.query_params.get("page", 1)
    query_page_number = int(query_page_number) if query_page_number != 1 else query_page_number
    page_size = 1
    page_offset = page_size * (query_page_number - 1)

    print(request.url)

    items = None

    if query_search_text and query_campuses and query_categories:
        items = list(queries.get_items_by_search_category_and_campus(categories=query_categories,
                                                campuses=query_campuses,
                                                search_text=query_search_text,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))

    elif query_search_text and query_campuses:
        items = list(queries.get_items_by_search_and_campus(campuses=query_campuses,
                                                search_text=query_search_text,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))
    elif query_search_text and query_categories:
        items = list(queries.get_items_by_search_and_category(categories=query_categories,
                                                search_text=query_search_text,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))
    elif query_categories and query_campuses:
        items = list(queries.get_items_by_category_and_campus(categories=query_categories,
                                                campuses=query_campuses,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))

    elif query_search_text:
        items = list(queries.get_items_by_search(search_text=query_search_text,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))
    elif query_categories:
        items = list(queries.get_items_by_category(categories=query_categories,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))

    elif query_campuses:
        items = list(queries.get_items_by_campus(campuses=query_campuses,
                                                sort_text=query_sort,
                                                limit=page_size,
                                                offset=page_offset
        ))
    else:
        items = list(queries.get_all_items(limit=page_size, offset=page_offset))

    # Pagination
    page = query_page_number
    total_items = items[0].get("total_count") if len(items) != 0 else 0
    page_total_items = len(items)
    total_pages = math.ceil(total_items / page_size)
    current_url = re.sub(r'([&?]page=\d+)|(page=\d+&?)', '', str(request.url)).strip("?").strip("&")
    current_url = current_url + "?" if current_url.split("/")[-1] == "search" else current_url

    context = {
        "items": items,
        "categories": {category["category_id"]:category["category_name"] for category in queries.get_all_categories()},
        "campuses": list(queries.get_all_campuses()),
        "form": {
            "search_text": query_search_text.replace("%", "") if query_search_text is not None else query_search_text,
            "campuses": query_campuses,
            "categories": query_categories,
            "sort": query_sort,
        },
        "pagination": {
            "page": page,
            "page_items_total": page_total_items,
            "items_total": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "current_url": current_url,
        }
    }

    return templates.TemplateResponse(request, "public/search_page.html", context)

@app.get("/search")
def reset_search(request: Request):

    context = {
        "categories": list(queries.get_all_categories()),
        "campuses": list(queries.get_all_campuses()),
        "items": list(queries.get_all_items()),
    }

    return templates.TemplateResponse(request, "public/search_page.html", context)

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