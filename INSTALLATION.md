codemxj/
   ├── analyzers/
   │   ├── __init__.py
   │   ├── code_parser.py
   │   ├── uml_generator.py
   │   ├── sequence_diagram.py
   │   ├── call_graph.py
   │   ├── project_analyzer.py
   │   ├── java_class.py
   │   ├── microservice_analyzer.py
   │   ├── legacy_table_analyzer.py
   │   ├── demographics_analyzer.py
   │   ├── integration_pattern_analyzer.py
   │   └── demographic_pattern_analyzer.py
   ├── utils/
   │   ├── __init__.py
   │   └── helpers.py
   ├── .streamlit/
   │   └── config.toml
   └── app.py
   ```

2. **Create Configuration Files**
   Create `.streamlit/config.toml` with:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   ```

3. **Install Required Packages**
   ```bash
   pip install streamlit==1.24.0
   pip install javalang==0.13.0
   pip install networkx==3.1
   pip install matplotlib==3.7.1
   pip install pandas==2.0.3
   pip install plantuml==0.3.0
   pip install plantuml-markdown
   ```

4. **Download Required Files**
   You'll need to download these core files:
   - `app.py` - Main application file (contains UI and analysis logic)
   - `analyzers/*.py` - Analysis modules for different aspects of code
   - `utils/helpers.py` - Utility functions for the application

5. **Configure Python Path**
   Ensure the project root directory is in your Python path:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/codemxj"
   ```

6. **Start the Application**
   ```bash
   cd codemxj
   streamlit run app.py
   ```
   The application will be available at `http://localhost:5000`

## Key Files Description

1. **app.py**
   - Main application file
   - Contains Streamlit UI code
   - Handles file upload and analysis coordination
   - Implements visualization logic

2. **analyzers/**
   - `code_parser.py` - Java code parsing functionality
   - `uml_generator.py` - UML diagram generation
   - `project_analyzer.py` - Project structure analysis
   - `java_class.py` - Java class model definitions
   - Other analyzers for specific features (microservices, patterns, etc.)

3. **utils/helpers.py**
   - Utility functions for code highlighting
   - File handling helpers
   - Progress bar implementations
   - Error handling utilities

## Verification

After installation, verify the following:
1. The web interface loads correctly at http://localhost:5000
2. You can upload a Java project ZIP file
3. The analysis tabs are visible and functional
4. UML diagram generation works
5. Project structure analysis completes successfully

## Troubleshooting

1. **Package Installation Issues**
   If you encounter any package installation errors:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --no-cache-dir
   ```

2. **Port Conflicts**
   If port 5000 is already in use:
   ```bash
   streamlit run app.py --server.port 5001