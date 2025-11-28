from __future__ import annotations
from typing import List, Tuple, Dict, Set
import numpy as np
from .models import Point

EARTH_RADIUS_KM = 6371.0088

def haversine_matrix(coords: np.ndarray) -> np.ndarray:
    lat = np.deg2rad(coords[:, 0])[:, None]
    lng = np.deg2rad(coords[:, 1])[:, None]
    lat_T = lat.T
    lng_T = lng.T
    dlat = lat - lat_T
    dlng = lng - lng_T
    a = np.sin(dlat/2.0)**2 + np.cos(lat)*np.cos(lat_T)*(np.sin(dlng/2.0)**2)
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return EARTH_RADIUS_KM * c

class UFDS:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0]*n
    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1
        return True

def edges_from_dist(dist: np.ndarray):
    n = dist.shape[0]
    out = []
    for i in range(n):
        for j in range(i+1, n):
            out.append((i, j, float(dist[i, j])))
    return out

def kruskal_mst(n: int, edges: List[Tuple[int,int,float]]):
    uf = UFDS(n)
    mst = []
    for (u, v, w) in sorted(edges, key=lambda e: e[2]):
        if uf.union(u, v):
            mst.append((u, v, w))
            if len(mst) == n-1:
                break
    return mst

def mst_to_adj(n: int, mst_edges: List[Tuple[int,int,float]]):
    adj: Dict[int, List[int]] = {i: [] for i in range(n)}
    for u, v, _ in mst_edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj

def dfs_preorder(adj: Dict[int, List[int]], start: int = 0) -> List[int]:
    order = []
    seen: Set[int] = set()
    stack = [start]
    while stack:
        u = stack.pop()
        if u in seen: 
            continue
        seen.add(u)
        order.append(u)
        for v in sorted(adj[u], reverse=True):
            if v not in seen:
                stack.append(v)
    return order

def route_geojson(points: List[Point], order: List[int], return_to_depot: bool) -> dict:
    coords = []
    for idx in order:
        p = points[idx]
        coords.append([p.lng, p.lat])
    if return_to_depot and len(order) > 1:
        coords.append([points[order[0]].lng, points[order[0]].lat])
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {"layer": "ROUTE", "ordered_indices": order},
            }
        ],
    }

def mst_geojson(points: List[Point], mst_edges: List[Tuple[int,int,float]]) -> dict:
    feats = []
    for u, v, w in mst_edges:
        a = points[u]; b = points[v]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[a.lng, a.lat], [b.lng, b.lat]]},
            "properties": {"layer":"MST","u":u,"v":v,"w":w}
        })
    return {"type":"FeatureCollection","features":feats}

def optimize_mst_mode(points: List[Point], return_to_depot: bool, avg_speed_kmh: float):
    # Build distance matrix
    coords = np.array([[p.lat, p.lng] for p in points], dtype=float)
    dist = haversine_matrix(coords)
    n = dist.shape[0]

    # MST (Kruskal + UFDS)
    edges = edges_from_dist(dist)
    mst = kruskal_mst(n, edges)

    # DFS preorder to get visiting order
    adj = mst_to_adj(n, mst)
    order = dfs_preorder(adj, start=0)

    # Build legs & KPIs
    legs = []
    total_km = 0.0
    total_min = 0.0
    for i in range(len(order)-1):
        d = float(dist[order[i], order[i+1]])
        t = (d / max(avg_speed_kmh, 1e-6)) * 60.0
        legs.append((order[i], order[i+1], d, t))
        total_km += d
        total_min += t
    if return_to_depot and len(order) > 1:
        d = float(dist[order[-1], order[0]])
        t = (d / max(avg_speed_kmh, 1e-6)) * 60.0
        legs.append((order[-1], order[0], d, t))
        total_km += d
        total_min += t

    return order, legs, total_km, total_min, mst
