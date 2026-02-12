
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory storage for logged hours (for demonstration purposes)
hours_data = []

@app.get("/health", response_class=HTMLResponse)
async def health_check(request: Request):
    return templates.TemplateResponse("health.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/log_time", response_class=HTMLResponse)
async def log_time(request: Request, date_str: str = Form(...), hours: float = Form(...), description: str = Form(...)):
    try:
        logged_date = date.fromisoformat(date_str)
        hours_data.append({"date": logged_date, "hours": hours, "description": description})
        return templates.TemplateResponse("index.html", {"request": request, "message": "Time logged successfully!"})
    except ValueError:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid date format. Please use YYYY-MM-DD."})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "hours_data": hours_data})

@app.post("/edit_time", response_class=HTMLResponse)
async def edit_time(request: Request, item_id: int = Form(...), date_str: str = Form(...), hours: float = Form(...), description: str = Form(...)):
    if 0 <= item_id < len(hours_data):
        try:
            logged_date = date.fromisoformat(date_str)
            hours_data[item_id] = {"date": logged_date, "hours": hours, "description": description}
            return templates.TemplateResponse("dashboard.html", {"request": request, "hours_data": hours_data, "message": "Entry updated successfully!"})
        except ValueError:
            return templates.TemplateResponse("dashboard.html", {"request": request, "hours_data": hours_data, "error": "Invalid date format. Please use YYYY-MM-DD."})
    return templates.TemplateResponse("dashboard.html", {"request": request, "hours_data": hours_data, "error": "Invalid item ID."})

@app.post("/delete_time", response_class=HTMLResponse)
async def delete_time(request: Request, item_id: int = Form(...)):
    if 0 <= item_id < len(hours_data):
        del hours_data[item_id]
        return templates.TemplateResponse("dashboard.html", {"request": request, "hours_data": hours_data, "message": "Entry deleted successfully!"})
    return templates.TemplateResponse("dashboard.html", {"request": request, "hours_data": hours_data, "error": "Invalid item ID."})

@app.get("/invoice", response_class=HTMLResponse)
async def invoice_form(request: Request):
    return templates.TemplateResponse("invoice.html", {"request": request})

@app.post("/generate_invoice", response_class=HTMLResponse)
async def generate_invoice(request: Request, client_name: str = Form(...), start_date: str = Form(...), end_date: str = Form(...)):
    # In a real application, you would filter hours_data by date range and generate a proper invoice document.
    # For this example, we'll just display a summary.
    try:
        start_d = date.fromisoformat(start_date)
        end_d = date.fromisoformat(end_date)
        filtered_hours = [h for h in hours_data if start_d <= h["date"] <= end_d]
        total_hours = sum(h["hours"] for h in filtered_hours)
        return templates.TemplateResponse("invoice.html", {
            "request": request,
            "client_name": client_name,
            "start_date": start_d,
            "end_date": end_d,
            "filtered_hours": filtered_hours,
            "total_hours": total_hours,
            "invoice_generated": True
        })
    except ValueError:
        return templates.TemplateResponse("invoice.html", {"request": request, "error": "Invalid date format. Please use YYYY-MM-DD."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
