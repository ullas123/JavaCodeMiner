# CodeMXJ Installation Guide

## Prerequisites

1. **Required Software**
   - Python 3.11 or higher
   - Java JDK 11 or higher (for analyzing Java source code)
   - pip (Python package manager)

## Installation Steps

1. **Install Required Packages**
   ```bash
   pip install streamlit==1.24.0
   pip install javalang==0.13.0
   pip install networkx==3.1
   pip install matplotlib==3.7.1
   pip install pandas==2.0.3
   pip install plantuml==0.3.0
   pip install plantuml-markdown
   ```

2. **Configuration Setup**
   Create a `.streamlit` directory and add `config.toml`:
   ```bash
   mkdir .streamlit
   ```
   
   Add to `.streamlit/config.toml`:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   ```

3. **Verify Installation**
   Run this command to verify all packages are installed correctly:
   ```bash
   python -c "import streamlit; import javalang; import networkx; import matplotlib; import pandas"
   ```

4. **Start the Application**
   ```bash
   streamlit run app.py
   ```
   The application will be available at `http://localhost:5000`

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
   ```

3. **Java-Related Errors**
   - Verify Java installation: `java -version`
   - Ensure JAVA_HOME is set correctly
   - Add Java to system PATH if needed

## Verification

After installation, verify the following:
1. The web interface loads correctly at http://localhost:5000
2. You can upload a Java project ZIP file
3. The analysis tabs are visible and functional
4. UML diagram generation works
5. Project structure analysis completes successfully

## Support

If you encounter any issues during installation:
1. Check the console for error messages
2. Verify all prerequisites are installed
3. Ensure all required ports are available
4. Check system permissions for file access
