/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Java** (required for PlantUML)
```bash
brew install openjdk
```

3. **Install PlantUML and Graphviz**
```bash
brew install plantuml
brew install graphviz
```

## Application Setup

1. **Clone the Repository**
```bash
git clone [repository-url]
cd codemxj
```

2. **Create Python Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate
```

3. **Install Required Python Packages**
```bash
pip install streamlit==1.24.0
pip install javalang==0.13.0
pip install networkx==3.1
pip install matplotlib==3.7.1
pip install pandas==2.0.3
pip install plantuml==0.3.0
pip install plantuml-markdown
```

4. **Verify Installation**
```bash
# Verify PlantUML installation
plantuml -version

# Verify Python packages
python -c "import streamlit; import javalang; import networkx; import matplotlib; import pandas"
```

## Running the Application

1. **Start the Application**
```bash
streamlit run app.py
```

2. **Access the Web Interface**
- Open your web browser
- Navigate to `http://localhost:5000`
- The application will automatically reload on code changes

## Mac-Specific Troubleshooting

1. **PlantUML Issues**
- Verify PlantUML is in your PATH:
```bash
which plantuml
```
- If needed, set PLANTUML_PATH environment variable:
```bash
export PLANTUML_PATH=$(which plantuml)
```
- Add to your shell profile (~/.zshrc or ~/.bash_profile):
```bash
echo 'export PLANTUML_PATH=$(which plantuml)' >> ~/.zshrc
source ~/.zshrc
```

2. **Port Conflicts**
If port 5000 is already in use (common with macOS AirPlay):
```bash
streamlit run app.py --server.port 5001
```

3. **Python Package Issues**
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

4. **Java Issues**
- Verify Java installation:
```bash
java -version
```
- If Java is not found, add it to your PATH:
```bash
echo 'export PATH="/usr/local/opt/openjdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

5. **M1/M2 Mac Issues**
If you're using an Apple Silicon Mac (M1/M2):
- Install Rosetta 2 if needed:
```bash
softwareupdate --install-rosetta
```
- Use native arm64 Python when possible:
```bash
arch -arm64 brew install python@3.11
```

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

## Common macOS Issues and Solutions

1. **Application Can't Be Opened**
   - If you see "app can't be opened because it is from an unidentified developer":
   - Go to System Preferences > Security & Privacy > General
   - Click "Open Anyway"

2. **Java Version Conflicts**
   - If you have multiple Java versions:
   ```bash
   # List installed Java versions
   /usr/libexec/java_home -V

   # Set specific version
   export JAVA_HOME=$(/usr/libexec/java_home -v 11)
   ```

3. **Network Access**
   - Allow incoming connections if prompted by macOS firewall
   - Configure firewall settings in System Preferences if needed

4. **Performance Issues**
   - Close unnecessary applications
   - Monitor CPU usage with Activity Monitor
   - Consider increasing Python's memory limit:
   ```bash
   export PYTHONMEMORY=4096
   ```