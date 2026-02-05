# Project Structure

## Directory Layout

```
.
├── .devcontainer/          # Development container configuration
│   └── devcontainer.json   # VS Code devcontainer settings
├── .kiro/                  # Kiro AI assistant configuration
│   └── steering/           # AI steering documents
├── app/                    # Main application directory
│   ├── .streamlit/         # Streamlit configuration
│   │   └── config.toml     # Streamlit settings
│   ├── pages/              # Streamlit multi-page app pages
│   ├── services/           # Backend API integration layer
│   ├── app.py              # Main entry point and dashboard
│   └── __init__.py
├── .gitignore
├── README.md
└── requirements.txt        # Python dependencies
```

## Application Architecture

### Entry Point
- **app/app.py**: Main dashboard with authentication, navigation, and analytics

### Pages (Multi-Page App)
Streamlit automatically discovers pages in the `app/pages/` directory:

- **login.py**: Authentication page
- **submissions.py**: Pending submission review interface (ADMIN only)
- **accepted_submissions.py**: View accepted submissions
- **rejected_submissions.py**: View rejected submissions
- **research_dataset.py**: Dataset export for research (REVIEWER access)
- **transactions.py**: Transaction management and payment tracking (ADMIN only)
- **export.py**: Export data for accountants (ADMIN only)

### Services Layer
- **app/services/api.py**: Centralized API client for backend communication
  - Authentication header management
  - Submission CRUD operations
  - Transaction operations
  - Dashboard analytics
  - Export functionality

## Code Organization Patterns

### Authentication Flow
1. Check for token in `st.session_state`
2. If missing, redirect to login page
3. Store token, role, and user info in session state after successful login
4. Use `_auth_headers()` helper for all API requests

### Page Structure
Each page follows this pattern:
1. Set page config with `st.set_page_config()`
2. Check authentication/authorization
3. Define helper functions for UI components
4. Implement main() function with page logic
5. Call main() in `if __name__ == "__main__"` block

### API Integration
- All API calls go through `app/services/api.py`
- Consistent error handling with `resp.raise_for_status()`
- Session state token automatically included in headers
- Base URL centralized in `API_BASE_URL` constant

### UI Components
- Custom metric cards using HTML/CSS in markdown
- Styled dataframes with pandas styling
- Expanders for collapsible content
- Custom CSS injected via `st.markdown()` with `unsafe_allow_html=True`

## Naming Conventions

- **Files**: snake_case (e.g., `research_dataset.py`)
- **Functions**: snake_case (e.g., `get_submissions_in_review()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **Session State Keys**: snake_case (e.g., `st.session_state.token`)
