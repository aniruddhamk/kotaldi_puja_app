from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kotaldi Puja Collection App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Calculate some stats for the dashboard
    total_amount = db.query(func.sum(models.Collection.amount)).scalar() or 0
    total_members = db.query(models.Collection.member_name).distinct().count()
    total_collections = db.query(models.Collection).count()
    
    # Get recent 5 collections
    recent_collections = db.query(models.Collection).order_by(models.Collection.created_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "total_amount": total_amount,
            "total_members": total_members,
            "total_collections": total_collections,
            "recent_collections": recent_collections,
        },
    )

@app.get("/add", response_class=HTMLResponse)
async def add_collection_form(request: Request):
    return templates.TemplateResponse("add_collection.html", {"request": request})

@app.post("/add")
async def add_collection(
    request: Request,
    month: str = Form(...),
    member_name: str = Form(...),
    amount: int = Form(...),
    db: Session = Depends(get_db)
):
    if amount < 0:
        return templates.TemplateResponse("add_collection.html", {"request": request, "error": "Amount cannot be negative."})
    
    new_collection = models.Collection(month=month.strip(), member_name=member_name.strip(), amount=amount)
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/view/monthly", response_class=HTMLResponse)
async def view_monthly(request: Request, month: str = "", db: Session = Depends(get_db)):
    total = 0
    records = []
    
    if month:
        records = db.query(models.Collection).filter(models.Collection.month.ilike(f"%{month.strip()}%")).all()
        total = sum(r.amount for r in records)
        
    return templates.TemplateResponse(
        "view_monthly.html",
        {
            "request": request,
            "month_searched": month,
            "total": total,
            "records": records
        }
    )

@app.get("/view/individual", response_class=HTMLResponse)
async def view_individual(request: Request, member_name: str = "", db: Session = Depends(get_db)):
    records = []
    total = 0
    
    if member_name:
        records = db.query(models.Collection).filter(models.Collection.member_name.ilike(f"%{member_name.strip()}%")).order_by(models.Collection.created_at.desc()).all()
        total = sum(r.amount for r in records)

    return templates.TemplateResponse(
        "view_individual.html",
        {
            "request": request,
            "member_searched": member_name,
            "records": records,
            "total": total
        }
    )
