from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
import pugsql
from dotenv import load_dotenv
import os
import math
import re
import secrets


app = FastAPI()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        staff_num: str = payload.get("sub")
        if staff_num is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        staff_details = queries.get_staff_details(staff_num=int(staff_num))
        if not staff_details:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return staff_details
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def verify_admin(user: dict = Depends(get_current_user)):
    if user.get("role_id") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return user


templates = Jinja2Templates(directory="src/templates")

queries = pugsql.module('src/sql/queries/')

supabase_connection = os.getenv("SUPABASE_CONNECTION_STRING")
queries.connect(supabase_connection)

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")

# Public pages

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
    page_size = 9
    page_offset = page_size * (query_page_number - 1)

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
        items = list(queries.get_all_items(limit=page_size, 
                                           sort_text=query_sort, 
                                           offset=page_offset))

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
    context = {
        "campuses": list(queries.get_all_campuses()),
    }

    return templates.TemplateResponse(request, "public/login.html", context)

@app.post("/login")
def login_post(request: Request, staff_num: str = Form(...), password: str = Form(...), role: str = Form(...)):
    campuses = list(queries.get_all_campuses())

    def error(msg: str):
        return templates.TemplateResponse(
            request, "public/login.html",
            {"error": msg, "campuses": campuses}
        )

    try:
        staff_num_int = int(staff_num)
    except ValueError:
        return error("Please enter a valid staff number.")

    staff = queries.get_staff_by_num(staff_num=staff_num_int)

    if not staff or not pwd_context.verify(password, staff["staff_password_hash"]):
        return error("Incorrect staff number or password.")

    if role == "ADMIN":
        if staff["role_id"] != "ADMIN":
            return error("You do not have administrator access.")
    else:
        if staff["role_id"] != "STAFF":
            return error("You do not have staff access.")

        assigned_campus_ids = [c["campus_id"] for c in queries.get_campuses_by_staff(staff_num=staff_num_int)]
        if role not in assigned_campus_ids:
            campus_name = next((c["campus_name"] for c in campuses if c["campus_id"] == role), role)
            return error(f"You are not assigned to the {campus_name} campus.")

    access_token = create_access_token(data={"sub": str(staff["staff_num"]), "role": staff["role_id"]})
    redirect_url = "/admin/dashboard" if staff["role_id"] == "ADMIN" else "/staff/dashboard"
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response

@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@app.get("/reset")
def reset(request: Request):
    return templates.TemplateResponse(request, "public/reset_password.html")

@app.post("/reset")
def reset_post(request: Request, staff_num: str = Form(...)):
    try:
        staff_num_int = int(staff_num)
    except ValueError:
        return templates.TemplateResponse(
            request, "public/reset_password.html",
            {"error": "Please enter a valid staff number."}
        )

    staff = queries.get_staff_by_num(staff_num=staff_num_int)
    if not staff:
        return templates.TemplateResponse(
            request, "public/reset_password.html",
            {"error": "No account found with that staff number."}
        )

    new_password = secrets.token_urlsafe(10)

    password_hash = pwd_context.hash(new_password)
    queries.update_staff_password(staff_num=staff_num_int, password_hash=password_hash)

    recipient_email = f"{staff_num_int}@nwu.ac.za"
    print("\n" + "="*60)
    print("="*60)
    print(f"  To:      {recipient_email}")
    print(f"  Subject: NWU Protection Services — Password Reset")
    print(f"")
    print(f"  Dear {staff['staff_fname']},")
    print(f"")
    print(f"  Your new password is: {new_password}")
    print("="*60 + "\n")

    return templates.TemplateResponse(
        request, "public/reset_password.html",
        {"success": f"A new password has been sent to {recipient_email}. Please check your university email."}
    )

# Staff pages

@app.get("/staff")
@app.get("/staff/dashboard")
def staff_dashboard(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "staff/dashboard.html", {"user": user})

@app.get("/staff/inventory")
def staff_inventory(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "staff/inventory.html", {"user": user})

@app.get("/staff/log-item")
def staff_log_item(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "staff/log_item.html", {"user": user})

@app.get("/staff/claim")
def staff_claim(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "staff/claim.html", {"user": user})

@app.get("/staff/claims")
def staff_claim_records(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "staff/claim_records.html", {"user": user})

@app.get("/staff/view-claim")
def staff_view_claim(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "staff/view_claim.html", {"user": user})


# Admin pages

@app.get("/admin")
@app.get("/admin/dashboard")
def admin_dashboard(request: Request, user: dict = Depends(verify_admin)):
    return templates.TemplateResponse(request, "admin/dashboard.html", {"user": user})

@app.get("/admin/inventory")
def admin_inventory(request: Request, user: dict = Depends(verify_admin)):
    return templates.TemplateResponse(request, "admin/inventory.html", {"user": user})

@app.get("/admin/analytics")
def admin_analytics(request: Request, user: dict = Depends(verify_admin)):
    return templates.TemplateResponse(request, "admin/analytics.html", {"user": user})
