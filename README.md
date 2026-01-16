# DramaFlux Backend (Django)

Django REST API for Jolibox drama streaming integration.

## Structure
```
dramaflux-backend/
├── dramaflux/        # Django settings
├── dramas/           # API app
│   ├── models.py     # JoliboxConfig model
│   ├── views.py      # API endpoints
│   ├── services.py   # Jolibox API client
│   └── admin.py      # Admin panel
├── manage.py
└── venv/             # Virtual environment
```

## Setup
```bash
cd dramaflux-backend
source venv/bin/activate
python manage.py runserver
```

## Admin
- URL: http://localhost:8000/admin/
- Login: `admin` / `admin123`
- Add Jolibox credentials here

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dramas/` | GET | List all dramas |
| `/api/dramas/{id}/` | GET | Drama details |
| `/api/dramas/{id}/episodes/` | GET | Episode list |

## CORS
CORS is enabled for all origins in development mode.
