from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
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
import urllib.parse
from supabase import create_client


app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_bucket = os.getenv("SUPABASE_BUCKET")
storage_client = create_client(supabase_url, supabase_key)

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
        user = dict(staff_details)
        user["campus_id"] = payload.get("campus")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def verify_admin(user: dict = Depends(get_current_user)):
    if user.get("role_id") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return user

def verify_staff(user: dict = Depends(get_current_user)):
    if user.get("role_id") != "STAFF":
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

@app.get("/home")
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
    current_url = re.sub(r'([&?]page=\d+)|(page=\d+[&?]?)', '', str(request.url)).strip("?").strip("&")
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
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            if role == "ADMIN":
                return RedirectResponse(url="/admin/dashboard")
            elif role == "STAFF":
                return RedirectResponse(url="/staff/dashboard")
        except jwt.PyJWTError:
            pass

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

    campus_id = role if staff["role_id"] == "STAFF" else None
    access_token = create_access_token(data={"sub": str(staff["staff_num"]), "role": staff["role_id"], "campus": campus_id})
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
def staff_dashboard(request: Request, user: dict = Depends(verify_staff)):
    campus_id = user["campus_id"]
    staff_num = user["staff_num"]

    logged_today = queries.get_items_logged_today_by_staff(staff_num=staff_num)
    claims_today = queries.get_claims_today_by_staff(staff_num=staff_num)
    in_storage = queries.get_items_in_storage_by_campus(campus_id=campus_id)

    page_size = 5
    recent_items = list(queries.get_items_by_campus_filtered(
        campus_id=campus_id,
        item_status=None,
        category_id=None,
        search_text=None,
        limit=page_size,
        offset=0,
    ))

    context = {
        "user": user,
        "stats": {
            "logged_today": logged_today,
            "claims_today": claims_today,
            "in_storage": in_storage,
        },
        "recent_items": recent_items,
    }
    return templates.TemplateResponse(request, "staff/dashboard.html", context)

@app.get("/staff/inventory")
def staff_inventory(request: Request, user: dict = Depends(verify_staff)):
    campus_id = user["campus_id"]

    query_search = request.query_params.get("search_text")
    query_search = f"%{query_search.strip()}%" if query_search and query_search.strip() else None

    query_status = request.query_params.get("status") or None
    raw_category = request.query_params.get("category_id")
    query_category = int(raw_category) if raw_category else None

    page = int(request.query_params.get("page", 1))
    page_size = 10
    offset = page_size * (page - 1)

    items = list(queries.get_items_by_campus_filtered(
        campus_id=campus_id,
        item_status=query_status,
        category_id=query_category,
        search_text=query_search,
        limit=page_size,
        offset=offset,
    ))

    total_items = items[0]["total_count"] if items else 0
    total_pages = math.ceil(total_items / page_size)

    context = {
        "user": user,
        "items": items,
        "categories": list(queries.get_all_categories()),
        "form": {
            "search_text": request.query_params.get("search_text", ""),
            "status": query_status,
            "category_id": query_category,
        },
        "pagination": {
            "page": page,
            "items_total": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        },
    }
    return templates.TemplateResponse(request, "staff/inventory.html", context)

@app.get("/staff/log-item")
def staff_log_item(request: Request, user: dict = Depends(verify_staff)):
    item_num = request.query_params.get("item_num")
    item = None
    if item_num:
        item = queries.get_item_by_num(item_num=int(item_num))
    context = {
        "user": user,
        "categories": list(queries.get_all_categories()),
        "item": item,
    }
    return templates.TemplateResponse(request, "staff/log_item.html", context)

@app.post("/staff/log-item")
async def staff_log_item_post(
    request: Request,
    user: dict = Depends(verify_staff),
    item_name: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(...),
    item_image: UploadFile = File(None),
    item_num: int = Form(None),
):
    image_url = None
    if item_image and item_image.filename:
        file_bytes = await item_image.read()
        ext = item_image.filename.rsplit(".", 1)[-1].lower()
        file_path = f"{user['campus_id']}/{secrets.token_hex(12)}.{ext}"
        storage_client.storage.from_(supabase_bucket).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": item_image.content_type},
        )
        image_url = storage_client.storage.from_(supabase_bucket).get_public_url(file_path)

    if item_num:
        queries.update_found_item(
            item_name=item_name,
            item_description=description,
            category_id=category_id,
            item_image_url=image_url,
            item_num=item_num,
        )
    else:
        queries.insert_found_item(
            item_name=item_name,
            item_description=description,
            item_date_received=datetime.now(timezone.utc),
            item_image_url=image_url,
            category_id=category_id,
            staff_num=user["staff_num"],
            campus_id=user["campus_id"],
        )

    return RedirectResponse(url="/staff/inventory", status_code=status.HTTP_302_FOUND)

@app.post("/staff/dispose")
def staff_dispose(
    request: Request,
    user: dict = Depends(verify_staff),
    item_num: int = Form(...),
):
    queries.update_item_status(item_num=item_num, item_status="disposed")
    return RedirectResponse(url="/staff/inventory", status_code=status.HTTP_302_FOUND)

@app.get("/staff/claim")
def staff_claim(request: Request, user: dict = Depends(verify_staff)):
    item_num = request.query_params.get("item_num")
    if not item_num:
        return RedirectResponse(url="/staff/inventory", status_code=status.HTTP_302_FOUND)

    item = queries.get_item_by_num(item_num=int(item_num))
    if not item or item["item_status"] != "in storage":
        return RedirectResponse(url="/staff/inventory", status_code=status.HTTP_302_FOUND)

    context = {
        "user": user,
        "item": item,
    }
    return templates.TemplateResponse(request, "staff/claim.html", context)

@app.post("/staff/claim")
def staff_claim_post(
    request: Request,
    user: dict = Depends(verify_staff),
    item_num: int = Form(...),
    claimant_num: int = Form(...),
    claimant_fname: str = Form(...),
    claimant_lname: str = Form(...),
    claimant_email: str = Form(...),
):
    queries.upsert_claimant(
        claimant_num=claimant_num,
        claimant_fname=claimant_fname.strip(),
        claimant_lname=claimant_lname.strip(),
        claimant_email=claimant_email,
    )

    claim_num = queries.insert_claim(
        claim_date=datetime.now(timezone.utc),
        item_num=item_num,
        staff_num=user["staff_num"],
        claimant_num=claimant_num,
    )

    queries.update_item_status(item_num=item_num, item_status="claimed")

    return RedirectResponse(url=f"/staff/view-claim?claim_num={claim_num}", status_code=status.HTTP_302_FOUND)

@app.get("/staff/claims")
def staff_claim_records(request: Request, user: dict = Depends(verify_staff)):
    campus_id = user["campus_id"]

    query_search = request.query_params.get("search_text")
    query_search = f"%{query_search.strip()}%" if query_search and query_search.strip() else None

    raw_month = request.query_params.get("month")
    query_year = int(raw_month.split("-")[0]) if raw_month else None
    query_month = int(raw_month.split("-")[1]) if raw_month else None

    page = int(request.query_params.get("page", 1))
    page_size = 10
    offset = page_size * (page - 1)

    claims = list(queries.get_claims_by_campus(
        campus_id=campus_id,
        search_text=query_search,
        year=query_year,
        month=query_month,
        limit=page_size,
        offset=offset,
    ))

    total_items = claims[0]["total_count"] if claims else 0
    total_pages = math.ceil(total_items / page_size)

    context = {
        "user": user,
        "claims": claims,
        "form": {
            "search_text": request.query_params.get("search_text", ""),
            "month": raw_month,
        },
        "pagination": {
            "page": page,
            "items_total": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        },
    }
    return templates.TemplateResponse(request, "staff/claim_records.html", context)

@app.get("/staff/view-claim")
def staff_view_claim(request: Request, user: dict = Depends(verify_staff)):
    claim_num = request.query_params.get("claim_num")
    item_num = request.query_params.get("item_num")

    if claim_num:
        claim = queries.get_claim_by_num(claim_num=int(claim_num))
    elif item_num:
        claim = queries.get_claim_by_item_num(item_num=int(item_num))
    else:
        return RedirectResponse(url="/staff/claims", status_code=status.HTTP_302_FOUND)

    if not claim:
        return RedirectResponse(url="/staff/claims", status_code=status.HTTP_302_FOUND)

    context = {
        "user": user,
        "claim": claim,
    }
    return templates.TemplateResponse(request, "staff/view_claim.html", context)


# Admin pages

@app.get("/admin")
@app.get("/admin/dashboard")
def admin_dashboard(request: Request, user: dict = Depends(verify_admin)):
    global_stats = queries.get_global_stats()
    campus_stats = list(queries.get_stats_by_campus())

    context = {
        "user": user,
        "global_stats": global_stats,
        "campus_stats": campus_stats,
    }
    return templates.TemplateResponse(request, "admin/dashboard.html", context)

@app.get("/admin/inventory")
def admin_inventory(request: Request, user: dict = Depends(verify_admin)):
    query_search = request.query_params.get("search_text")
    query_search = f"%{query_search.strip()}%" if query_search and query_search.strip() else None

    query_campus = request.query_params.get("campus_id") or None
    query_status = request.query_params.get("status") or None
    raw_category = request.query_params.get("category_id")
    query_category = int(raw_category) if raw_category else None

    page = int(request.query_params.get("page", 1))
    page_size = 10
    offset = page_size * (page - 1)

    items = list(queries.get_admin_items_filtered(
        campus_id=query_campus,
        item_status=query_status,
        category_id=query_category,
        search_text=query_search,
        limit=page_size,
        offset=offset,
    ))

    total_items = items[0]["total_count"] if items else 0
    total_pages = math.ceil(total_items / page_size)

    context = {
        "user": user,
        "items": items,
        "categories": list(queries.get_all_categories()),
        "campuses": list(queries.get_all_campuses()),
        "form": {
            "search_text": request.query_params.get("search_text", ""),
            "campus_id": query_campus,
            "status": query_status,
            "category_id": query_category,
        },
        "pagination": {
            "page": page,
            "items_total": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        },
    }
    return templates.TemplateResponse(request, "admin/inventory.html", context)

@app.get("/admin/analytics")
def admin_analytics(request: Request, user: dict = Depends(verify_admin)):
    raw_year = request.query_params.get("year")
    raw_quarter = request.query_params.get("quarter")
    query_campus = request.query_params.get("campus_id") or None

    query_year = int(raw_year) if raw_year else None
    quarter_map = {"q1": 1, "q2": 2, "q3": 3, "q4": 4}
    query_quarter = quarter_map.get(raw_quarter) if raw_quarter else None

    summary = queries.get_analytics_summary(
        campus_id=query_campus,
        year=query_year,
        quarter=query_quarter,
    )
    most_lost = queries.get_most_lost_category(
        campus_id=query_campus,
        year=query_year,
        quarter=query_quarter,
    )
    category_dist = list(queries.get_category_distribution(
        campus_id=query_campus,
        year=query_year,
        quarter=query_quarter,
    ))
    campus_volume = list(queries.get_campus_volume(
        year=query_year,
        quarter=query_quarter,
    ))
    monthly_trend = list(queries.get_monthly_trend(
        campus_id=query_campus,
        year=query_year,
        quarter=query_quarter,
    ))

    context = {
        "user": user,
        "campuses": list(queries.get_all_campuses()),
        "summary": summary,
        "most_lost": most_lost,
        "category_dist": category_dist,
        "campus_volume": campus_volume,
        "monthly_trend": monthly_trend,
        "form": {
            "year": raw_year or "",
            "quarter": raw_quarter or "",
            "campus_id": query_campus,
        },
    }
    return templates.TemplateResponse(request, "admin/analytics.html", context)

@app.get("/admin/categories")
def admin_categories(request: Request, user: dict = Depends(verify_admin)):
    categories = list(queries.get_all_categories_with_counts())
    context = {
        "user": user,
        "categories": categories,
    }
    return templates.TemplateResponse(request, "admin/categories.html", context)

@app.post("/admin/categories")
def admin_categories_post(
    request: Request,
    user: dict = Depends(verify_admin),
    category_name: str = Form(...),
):
    def render_cat_page(error_msg=None, success_msg=None):
        categories = list(queries.get_all_categories_with_counts())
        context = {
            "request": request,
            "user": user,
            "categories": categories,
            "error": error_msg,
            "success": success_msg,
        }
        return templates.TemplateResponse(request, "admin/categories.html", context)

    cleaned_name = category_name.strip()
    if not cleaned_name:
        return render_cat_page(error_msg="Category name cannot be empty")
    
    existing = queries.get_category_by_name(category_name=cleaned_name)
    if existing:
        return render_cat_page(error_msg="Category already exists")
    
    queries.insert_category(category_name=cleaned_name)
    return render_cat_page(success_msg="Category created successfully")

@app.post("/admin/categories/delete")
def admin_categories_delete(
    request: Request,
    user: dict = Depends(verify_admin),
    category_id: int = Form(...),
):
    def render_cat_page(error_msg=None, success_msg=None):
        categories = list(queries.get_all_categories_with_counts())
        context = {
            "request": request,
            "user": user,
            "categories": categories,
            "error": error_msg,
            "success": success_msg,
        }
        return templates.TemplateResponse(request, "admin/categories.html", context)

    count = queries.count_items_by_category(category_id=category_id)
    if count > 0:
        return render_cat_page(error_msg="Cannot delete category referenced by items")
    
    queries.delete_category(category_id=category_id)
    return render_cat_page(success_msg="Category deleted successfully")

@app.get("/admin/staff")
def admin_staff(request: Request, user: dict = Depends(verify_admin)):
    staff_list = list(queries.get_all_staff_details())
    campuses = list(queries.get_all_campuses())
    context = {
        "user": user,
        "staff_list": staff_list,
        "campuses": campuses,
    }
    return templates.TemplateResponse(request, "admin/staff.html", context)

@app.post("/admin/staff")
async def admin_staff_post(
    request: Request,
    user: dict = Depends(verify_admin),
):
    form_data = await request.form()

    def render_staff_page(error_msg=None, success_msg=None):
        staff_list = list(queries.get_all_staff_details())
        campuses = list(queries.get_all_campuses())
        context = {
            "request": request,
            "user": user,
            "staff_list": staff_list,
            "campuses": campuses,
            "error": error_msg,
            "success": success_msg,
        }
        return templates.TemplateResponse(request, "admin/staff.html", context)

    try:
        staff_num = int(form_data.get("staff_num"))
    except (ValueError, TypeError):
        return render_staff_page(error_msg="Invalid staff number")
    
    staff_fname = form_data.get("staff_fname", "").strip()
    staff_lname = form_data.get("staff_lname", "").strip()
    role_id = form_data.get("role_id", "").strip()
    campus_id = form_data.get("campus_id", "").strip()

    if not staff_fname or not staff_lname or not role_id:
        return render_staff_page(error_msg="Missing required fields")

    existing = queries.get_staff_by_num(staff_num=staff_num)
    if existing:
        return render_staff_page(error_msg="Account with this staff number already exists")

    staff_email = f"{staff_num}@nwu.ac.za"

    if role_id == "STAFF" and not campus_id:
        return render_staff_page(error_msg="STAFF role requires assignment to a campus")

    new_password = secrets.token_urlsafe(10)
    password_hash = pwd_context.hash(new_password)

    try:
        queries.insert_staff(
            staff_num=staff_num,
            staff_fname=staff_fname,
            staff_lname=staff_lname,
            staff_email=staff_email.lower(),
            staff_password_hash=password_hash,
            role_id=role_id,
        )
    except Exception as e:
        return render_staff_page(error_msg="Could not create account. Database error.")

    if role_id == "STAFF":
        queries.insert_campus_assignment(staff_num=staff_num, campus_id=campus_id)

    print("\n" + "="*60)
    print(f"Subject: NWU Protection Services Account Provisioned")
    print(f"Dear {staff_fname} {staff_lname},")
    print(f"An account has been created for you on the Lost and Found System.")
    print(f"Your login credentials are:")
    print(f"Staff Number: {staff_num}")
    print(f"Password: {new_password}")
    print(f"Role: {role_id}")
    print("="*60 + "\n")

    return render_staff_page(success_msg=f"Staff account #{staff_num} successfully created.")

@app.post("/admin/staff/update-campus")
def admin_staff_update_campus(
    request: Request,
    user: dict = Depends(verify_admin),
    staff_num: int = Form(...),
    campus_id: str = Form(...),
):
    def render_staff_page(error_msg=None, success_msg=None):
        staff_list = list(queries.get_all_staff_details())
        campuses = list(queries.get_all_campuses())
        context = {
            "request": request,
            "user": user,
            "staff_list": staff_list,
            "campuses": campuses,
            "error": error_msg,
            "success": success_msg,
        }
        return templates.TemplateResponse(request, "admin/staff.html", context)

    target_staff = queries.get_staff_by_num(staff_num=staff_num)
    if not target_staff:
        return render_staff_page(error_msg="Personnel account not found")

    if target_staff.get("role_id") == "ADMIN":
        return render_staff_page(error_msg="Administrators possess global scope. Campus reassignment inapplicable.")

    queries.delete_campus_assignments(staff_num=staff_num)
    queries.insert_campus_assignment(staff_num=staff_num, campus_id=campus_id)

    return render_staff_page(success_msg="Personnel campus assignment successfully updated")


