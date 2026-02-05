# Technology Stack

## Framework & Runtime

- **Python 3.11**: Primary runtime environment
- **Streamlit 1.49.1**: Web application framework for building the dashboard UI

## Key Dependencies

### Data Processing
- **pandas 2.3.2**: Data manipulation and analysis
- **numpy 2.3.2**: Numerical computing
- **pyarrow 21.0.0**: Columnar data format support

### Visualization
- **altair 5.5.0**: Declarative statistical visualization
- **pydeck 0.9.1**: WebGL-powered data visualization

### HTTP & API
- **requests 2.32.5**: HTTP library for API communication
- **urllib3 2.5.0**: HTTP client

### Utilities
- **python-dateutil 2.9.0**: Date/time parsing
- **Pillow 11.3.0**: Image processing
- **GitPython 3.1.45**: Git repository interaction

## Backend Integration

- **API Base URL**: `https://api.knoxxi.net/knoxxi-uriscan`
- **Authentication**: JWT Bearer token stored in Streamlit session state
- **API Communication**: RESTful endpoints using `requests` library

## Development Environment

### DevContainer Configuration
- Base image: `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`
- Auto-installs dependencies from `requirements.txt` on container creation
- VS Code extensions: Python, Pylance

### Running the Application

**Start Development Server:**
```bash
streamlit run app/app.py --server.enableCORS false --server.enableXsrfProtection false
```

**Default Port:** 8501

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

### DevContainer Auto-Start
The devcontainer is configured to automatically start the Streamlit server on port 8501 when attached.

## Configuration

### Streamlit Config
Located at `app/.streamlit/config.toml` - contains Streamlit-specific settings for theming and behavior.

### Session State Management
- Authentication tokens stored in `st.session_state`
- User role and profile information persisted across page navigation
- Selected submission tracking for detail views
