# factory-class-crud-generator: Auto-Generated CRUD API

factory-class-crud-generator is a Python FastAPI application that automatically discovers model classes in a models directory, creates PostgreSQL database tables, and generates complete CRUD endpoints with OpenAPI documentation.

## Features

- **Automatic Model Discovery**: Automatically finds and registers all model classes in the `models/` directory
- **Dynamic Table Creation**: Creates PostgreSQL tables based on SQLAlchemy model definitions
- **Auto-Generated CRUD Endpoints**: Generates complete Create, Read, Update, Delete endpoints for each model
- **OpenAPI Documentation**: Provides interactive API documentation at `/docs` and `/redoc`
- **Type Safety**: Uses Pydantic for request/response validation
- **Comprehensive Testing**: Includes full test suite with pytest
- **Easy Extension**: Simply add new model files to automatically get new API endpoints

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- pip

### Installation

1. Clone or download the project:
```bash
git clone <repository-url>
cd factory-class-crud-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres createdb api_ad
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"
```

4. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your database settings
```

5. Run the application:
```bash
python main.py
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage

### Adding New Models

To add a new model and automatically get CRUD endpoints:

1. Create a new Python file in the `models/` directory
2. Define your model class inheriting from `BaseModel`
3. Restart the application

Example model (`models/blog_post.py`):

```python
from sqlalchemy import Column, String, Text, Boolean
from models.base import BaseModel

class BlogPost(BaseModel):
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    published = Column(Boolean, default=False, nullable=False)
    author = Column(String(100), nullable=False)
```

This will automatically create:
- Database table: `blog_posts`
- API endpoints:
  - `POST /blogpost/` - Create new blog post
  - `GET /blogpost/` - List all blog posts (with pagination)
  - `GET /blogpost/{id}` - Get specific blog post
  - `PUT /blogpost/{id}` - Update blog post
  - `DELETE /blogpost/{id}` - Delete blog post

### API Endpoints

All models automatically get the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/{model}/` | Create new item |
| GET | `/{model}/` | List all items (supports `skip` and `limit` query params) |
| GET | `/{model}/{id}` | Get item by ID |
| PUT | `/{model}/{id}` | Update item by ID |
| DELETE | `/{model}/{id}` | Delete item by ID |

### Example API Usage

```bash
# Create a new user
curl -X POST "http://localhost:8000/user/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "is_active": true
  }'

# Get all users
curl "http://localhost:8000/user/"

# Get user by ID
curl "http://localhost:8000/user/1"

# Update user
curl -X PUT "http://localhost:8000/user/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "age": 31
  }'

# Delete user
curl -X DELETE "http://localhost:8000/user/1"
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/api_ad
POSTGRES_DB=example
POSTGRES_USER=example
POSTGRES_PASSWORD=pass

# API Configuration
API_TITLE=factory-class-crud-generator
API_DESCRIPTION=Auto-generated CRUD API from model classes
API_VERSION=1.0.0

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Model Discovery
MODELS_DIR=models
```

### Database Configuration

The application uses PostgreSQL by default. You can modify the database URL in the `.env` file or set the `DATABASE_URL` environment variable.

## Project Structure

```
factory-class-crud-generator/
├── app/
│   ├── __init__.py
│   ├── config.py              # Application configuration
│   ├── database.py            # Database setup and connection
│   ├── model_discovery.py     # Automatic model discovery
│   └── crud_generator.py      # Dynamic CRUD endpoint generation
├── models/
│   ├── __init__.py
│   ├── base.py               # Base model class
│   ├── offer.py              # Example Offer model
│   ├── product.py            # Example Product model
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
└── README.md                # This file
```

## How It Works

1. **Model Discovery**: On startup, the application scans the `models/` directory for Python files
2. **Class Detection**: Finds all classes that inherit from `BaseModel`
3. **Table Creation**: Uses SQLAlchemy to create database tables based on model definitions
4. **Endpoint Generation**: Dynamically creates FastAPI routes for each model
5. **Documentation**: Automatically generates OpenAPI documentation with proper schemas

## Deployment

### Local Development

```bash
python main.py
```

### Production Deployment

1. **Using Uvicorn directly**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

2. **Using Docker** (create Dockerfile):
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. **Environment Variables for Production**:
```env
DATABASE_URL=postgresql://user:password@db-host:5432/api_ad
DEBUG=false
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

