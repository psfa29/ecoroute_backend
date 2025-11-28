from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from .models import OptimizeRequest, OptimizeResponse, Leg, Point, UserRegister, UserLogin
from .optimizer_mst import optimize_mst_mode, route_geojson, mst_geojson

app = FastAPI(title="EcoRoute MST Optimizer", version="0.1.0")

# Base de datos simulada en memoria con usuarios existentes
fake_users_db: List[Dict] = [
    {
        "username": "dorian",
        "password": "admin123",
        "email": "dorian@ecoroute.com",
        "fullName": "Dorian EcoRoute"
    },
    {
        "username": "admin",
        "password": "pass123",
        "email": "admin@ecoroute.com",
        "fullName": "Administrador Principal"
    },
    {
        "username": "tester",
        "password": "testpass",
        "email": "tester@ecoroute.com",
        "fullName": "Usuario de Prueba"
    },
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/register", status_code=201)
def register_user(user: UserRegister):
    # NOTA EDUCATIVA: En la vida real, NUNCA se debe guardar contraseñas en texto plano.
    
    for u in fake_users_db:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    new_user = user.dict()
    fake_users_db.append(new_user)
    
    return {"message": "Usuario registrado exitosamente"}

@app.post("/api/login")
def login_user(user: UserLogin):
    found_user = None
    for u in fake_users_db:
        if u["username"] == user.username and u["password"] == user.password:
            found_user = u
            break
    
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    
    return {
        "token": "token-falso-educativo", 
        "username": found_user["username"],
        "fullName": found_user["fullName"]
    }

@app.post("/optimize_mst", response_model=OptimizeResponse)
def optimize_mst(req: OptimizeRequest):
    points = [req.depot] + req.stops
    order, legs_raw, total_km, total_min, mst_edges = optimize_mst_mode(points, req.return_to_depot, req.average_speed_kmh)
    legs = [Leg(from_index=f, to_index=t, distance_km=round(d,4), duration_min=round(tm,2)) for (f,t,d,tm) in legs_raw]
    co2_kg = round(total_km * req.liters_per_km * 2.68, 3)
    route_gj = route_geojson(points, order, req.return_to_depot)
    mst_gj = mst_geojson(points, mst_edges)
    return OptimizeResponse(
        order=order,
        legs=legs,
        total_distance_km=round(total_km,4),
        total_duration_min=round(total_min,2),
        co2_kg=co2_kg,
        geojson=route_gj,
        mst_geojson=mst_gj
    )