=====================
Viet Nam province API
=====================

Homepage: https://provinces.open-api.vn

This is a FastAPI-based REST API providing standardized data about Vietnamese provinces, districts, and wards. 
Built on top of the VietnamProvinces_ library, it helps developers access Vietnamese administrative division data 
through a clean HTTP API interface.

Features:
- Complete data for all Vietnamese provinces, districts, and wards
- Two API versions (v1 and v2) with different data structures
- Search functionality for provinces, districts, and wards
- Address parsing from Vietnamese address strings
- Unicode and non-unicode search support
- Rate limiting and client filtering
- Docker support for easy deployment

Quick Start (Docker)
--------------------

The fastest way to get started:

.. code-block:: sh

   # Clone repository
   git clone <repo-url>
   cd vn-open-api-provinces
   
   # Start with Docker Compose
   docker-compose up -d
   
   # Or use quick-start script
   chmod +x quick-start.sh
   ./quick-start.sh

Access API at http://localhost:8000/docs

Development guide
-----------------

This is a Python FastAPI application. To get started:

**Prerequisites:**
- Python 3.12+
- UV package manager (recommended) or pip

**Setup:**

1. Install dependencies:

   .. code-block:: sh

     # Using UV (recommended)
     uv install
     
     # Or using pip
     pip install -e .

2. Run the development server:

   .. code-block:: sh

     # Using UV
     uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
     
     # Or using just
     just dev-server-uvicorn
     
     # Or using granian (faster)
     just dev-server

3. Access the API:
   - API Documentation: http://localhost:8000/docs
   - API v1: http://localhost:8000/api/v1/
   - API v2: http://localhost:8000/api/v2/

**API Endpoints:**

- ``GET /api/v1/`` - List all provinces (v1 format)
- ``GET /api/v1/p/{code}`` - Get province by code
- ``GET /api/v1/d/{code}`` - Get district by code  
- ``GET /api/v1/w/{code}`` - Get ward by code
- ``GET /api/v2/`` - List all provinces (v2 format)
- ``GET /api/v2/p/{code}`` - Get province with wards
- ``GET /api/v2/w/{code}`` - Get ward by code
