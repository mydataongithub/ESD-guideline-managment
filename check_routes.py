# check_routes.py
"""Check registered routes in the FastAPI application"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

print("Registered routes in the application:")
print("=" * 60)

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        for method in route.methods:
            routes.append((method, route.path, route.name))

# Sort by path
routes.sort(key=lambda x: x[1])

# Print routes
for method, path, name in routes:
    print(f"{method:6} {path:40} {name}")
    
# Check specifically for template routes
print("\n" + "=" * 60)
print("Routes containing 'template':")
for method, path, name in routes:
    if 'template' in path.lower():
        print(f"{method:6} {path:40} {name}")
        
# Check for endpoints starting with /select
print("\n" + "=" * 60)
print("Routes starting with '/select':")
for method, path, name in routes:
    if path.startswith('/select'):
        print(f"{method:6} {path:40} {name}")
