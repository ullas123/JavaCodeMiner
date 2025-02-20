git clone [repository-url]
   cd codemxj
   ```

2. **Create and Activate Python Environment** (Recommended)
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on Windows
   .\venv\Scripts\activate

   # Activate on Unix/MacOS
   source venv/bin/activate
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

   Required packages and versions:
   - streamlit (1.24.0+) - Web interface framework
   - javalang (0.13.0+) - Java source code parser
   - networkx (3.1+) - Graph analysis and visualization
   - matplotlib (3.7+) - Plotting and visualization
   - pandas (2.0+) - Data manipulation
   - plantuml (0.3.0+) - UML diagram generation
   - plantuml-markdown - Documentation support

4. **Verify Installation**
   ```bash
   python -c "import streamlit; import javalang; import networkx; import matplotlib; import pandas"
   ```

### Running the Application

1. **Start the Application**
   ```bash
   streamlit run app.py
   ```

2. **Access the Web Interface**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - The application will automatically reload on code changes

### Usage Instructions

1. Upload your Java project:
   - Package your Java project as a ZIP file
   - Use the upload button in the application
   - Only .java files will be processed

2. Navigate through analysis tabs:
   - Code Structure - View project organization
   - Diagrams - UML and dependency visualizations
   - Integration Patterns - Service communication analysis
   - Demographics - Usage and distribution patterns
   - Service Graph - Microservice interactions
   - API Details - Endpoint documentation
   - Legacy API Analysis - Compatibility checking
   - Database - Data interaction analysis
   - Analysis Summary - Overall project insights

### Troubleshooting

1. **Package Installation Issues**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --no-cache-dir
   ```

2. **Java-Related Errors**
   - Verify Java installation: `java -version`
   - Check JAVA_HOME environment variable
   - Ensure Java binary is in system PATH

3. **Port Conflicts**
   - Default port is 5000
   - To use a different port:
     ```bash
     streamlit run app.py --server.port [YOUR_PORT]