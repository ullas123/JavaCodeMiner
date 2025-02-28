import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import os
import tempfile
import pandas as pd
from zipfile import ZipFile
from analyzers.code_parser import JavaCodeParser
from analyzers.uml_generator import UMLGenerator
from analyzers.sequence_diagram import SequenceDiagramGenerator
from analyzers.call_graph import CallGraphAnalyzer
from analyzers.project_analyzer import ProjectAnalyzer
from utils.helpers import display_code_with_syntax_highlighting, create_download_link, show_progress_bar, handle_error
from analyzers.java_class import JavaClass
import base64
from io import BytesIO
from analyzers.microservice_analyzer import MicroserviceAnalyzer
from analyzers.legacy_table_analyzer import LegacyTableAnalyzer
from analyzers.demographics_analyzer import DemographicsAnalyzer
from analyzers.integration_pattern_analyzer import IntegrationPatternAnalyzer
from analyzers.demographic_pattern_analyzer import DemographicPatternAnalyzer
import re

st.set_page_config(
    page_title="CodeMXJ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def extract_project(uploaded_file):
    """Extract uploaded zip file to temporary directory"""
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()

    temp_dir = st.session_state.temp_dir

    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    try:
        with ZipFile(uploaded_file, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('/'):
                    continue
                if file_info.filename.endswith('.java'):
                    zip_ref.extract(file_info, temp_dir)

        st.session_state.project_files = [
            f for f in os.listdir(temp_dir)
            if f.endswith('.java') and os.path.isfile(os.path.join(temp_dir, f))
        ]
        return temp_dir
    except Exception as e:
        st.error(f"Error extracting project: {str(e)}")
        return None


def main():
    st.title("CodeMXJ")
    st.markdown("<p style='color: #B8860B;'>Advanced Java Code Analysis & Visualization</p>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("Explore Java Code ☕")

        st.header("Upload Project")
        uploaded_file = st.file_uploader(
            "Upload Java Project (ZIP file containing .java files)",
            type=["zip"],
            help="Upload a ZIP file containing Java source files (.java)"
        )

        st.markdown("---")
        st.markdown("""
        <div style='width: 100%;'>
            <div style='background-color: #28a745; color: white; padding: 8px; text-align: center; border-radius: 5px 5px 0 0;'>
                <span style='font-size: 14px;'>Design & Development</span>
            </div>
            <div style='background-color: white; padding: 10px; border: 1px solid #28a745; border-radius: 0 0 5px 5px;'>
                <p style='margin: 0; text-align: center; color: #666;'>Zensar Diamond Team</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    structure_tab, diagrams_tab, patterns_tab, demographics_tab, services_tab, api_details_tab, legacy_api_tab, db_tab, analysis_tab = st.tabs([
        "Code Structure", "Diagrams", "Integration Patterns", "Demographics",
        "Service Graph", "API Details", "Legacy API Analysis", "Database", "Analysis Summary"
    ])

    if uploaded_file is not None:
        try:
            project_path = extract_project(uploaded_file)

            st.write("Project Info:")
            st.write("✓ Project loaded successfully")

            with st.spinner('Analyzing project structure...'):
                analyzer = ProjectAnalyzer()
                ms_analyzer = MicroserviceAnalyzer()
                legacy_analyzer = LegacyTableAnalyzer()
                demo_analyzer = DemographicsAnalyzer()
                int_analyzer = IntegrationPatternAnalyzer()
                pattern_analyzer = DemographicPatternAnalyzer()

                java_files = analyzer.analyze_project(project_path)
                if not java_files:
                    st.warning(f"No Java files found in the uploaded project")
                    return

                for file in java_files:
                    file_path = os.path.join(project_path, file.path)
                    service_name = file.path.split('/')[0] if '/' in file.path else 'default'

                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        ms_analyzer.analyze_code(code, service_name)
                        legacy_analyzer.analyze_code(file_path, code)
                        demo_analyzer.analyze_code(file_path, code)
                        int_analyzer.analyze_code(file_path, code)
                        pattern_analyzer.analyze_code(file_path, code)

                project_structure = analyzer.get_project_structure(java_files)

            with structure_tab:
                col1, col2 = st.columns([2, 1])
                with col1:
                    display_project_structure(project_structure)

                st.divider()

            with diagrams_tab:
                display_diagrams_summary(java_files)


            with legacy_api_tab:
                st.subheader("Legacy API & Table Analysis")
                legacy_overview, table_list = st.tabs(["API Overview", "Legacy Tables"])

                with legacy_overview:
                    try:
                        api_details = ms_analyzer.get_api_details()
                        if not api_details:
                            st.info("No API endpoints found using legacy tables")
                        else:
                            for service, endpoints in api_details.items():
                                with st.expander(f"Service: {service}", expanded=True):
                                    for endpoint in endpoints:
                                        if endpoint['legacy_tables']:
                                            st.markdown(f"""
                                            ### {endpoint['method']} {endpoint['path']}
                                            **Handler:** `{endpoint['class']}.{endpoint['handler']}`

                                            **Legacy Tables Used:**
                                            {', '.join(endpoint['legacy_tables'])}

                                            **Request Parameters:**
                                            {', '.join(endpoint['request_params']) if endpoint['request_params'] else 'None'}

                                            **Response Fields:**
                                            {', '.join(endpoint['response_fields']) if endpoint['response_fields'] else 'None'}
                                            """)
                                            st.markdown("---")
                    except Exception as e:
                        st.error(f"Error analyzing legacy APIs: {str(e)}")

                with table_list:
                    st.subheader("Legacy Database Tables")
                    try:
                        legacy_tables = legacy_analyzer.get_legacy_tables()
                        if legacy_tables:
                            for schema, tables in legacy_tables.items():
                                with st.expander(f"Schema: {schema}", expanded=True):
                                    for table in tables:
                                        st.markdown(f"""
                                        ### {table['name']}
                                        **Description:** {table.get('description', 'No description available')}

                                        **Usage Count:** {table.get('usage_count', 0)} references

                                        **Used By Services:**
                                        {', '.join(table.get('used_by', ['No services']))}
                                        """)
                        else:
                            st.info("No legacy tables found in the analysis")
                    except Exception as e:
                        st.error(f"Error analyzing legacy tables: {str(e)}")

            with services_tab:
                st.subheader("Service-to-Service Interaction Analysis")

                with st.spinner('Analyzing microservice interactions...'):
                    viz_type = st.radio(
                        "Select Visualization",
                        ["Service Dependency Graph", "API Interaction Map", "Service Matrix"]
                    )

                    if viz_type == "Service Dependency Graph":
                        graph, graph_data = ms_analyzer.generate_service_graph()

                        fig, ax = plt.subplots(figsize=(12, 8))
                        pos = graph_data['positions']

                        nx.draw_networkx_nodes(graph, pos,
                                                node_color='lightblue',
                                                node_size=2000)

                        edge_colors = {
                            'feign': 'blue',
                            'rest': 'green',
                            'kafka': 'red',
                            'database': 'purple'
                        }

                        for u, v, data in graph_data['edges']:
                            edge_type = data.get('type', 'rest')
                            nx.draw_networkx_edges(graph, pos,
                                                    edgelist=[(u, v)],
                                                    edge_color=edge_colors.get(edge_type, 'gray'),
                                                    style='dashed' if edge_type == 'kafka' else 'solid')

                        nx.draw_networkx_labels(graph, pos)

                        buf = BytesIO()
                        plt.savefig(buf, format='png', bbox_inches='tight')
                        buf.seek(0)
                        st.image(buf, caption="Service Dependency Graph", width=None)

                        st.markdown("""
                        **Legend:**
                        - Blue edges: Feign Client connections
                        - Green edges: REST API calls
                        - Red dashed edges: Kafka events
                        - Purple edges: Database interactions
                        """)

            with api_details_tab:
                st.subheader("API Analysis")
                api_type = st.radio(
                    "Select API Type",
                    ["REST APIs", "SOAP Services"]
                )

                if api_type == "REST APIs":
                    with st.spinner('Analyzing REST APIs...'):
                        rest_details = ms_analyzer.get_rest_api_details()

                        if not rest_details:
                            st.info("No REST APIs found in the project")
                        else:
                            for service, apis in rest_details.items():
                                with st.expander(f"Service: {service}", expanded=True):
                                    for api in apis:
                                        st.markdown(f"""
                                        ### {api['method']} {api['path']}
                                        **Handler:** `{api['class']}.{api['handler']}`

                                        **Client Type:** {api['client_type']}
                                        (RestTemplate/FeignClient/Direct Controller)

                                        **Request Parameters:**
                                        {', '.join(api['request_params']) if api['request_params'] else 'None'}

                                        **Response Type:**
                                        {', '.join(api['response_fields']) if api['response_fields'] else 'None'}

                                        **Called Services:**
                                        {', '.join(api['called_services']) if api['called_services'] else 'None'}
                                        """)
                                        st.markdown("---")

                else:
                    with st.spinner('Analyzing SOAP Services...'):
                        soap_details = ms_analyzer.get_soap_service_details()

                        if not soap_details:
                            st.info("No SOAP services found in the project")
                        else:
                            for service, operations in soap_details.items():
                                with st.expander(f"Service: {service}", expanded=True):
                                    for op in operations:
                                        st.markdown(f"""
                                        ### {op['operation_name']}
                                        **Service Interface:** `{op['interface']}`

                                        **WSDL Location:** {op['wsdl_location']}

                                        **Input Parameters:**
                                        {', '.join(op['input_params']) if op['input_params'] else 'None'}

                                        **Output Type:**
                                        {op['output_type']}
                                        """)
                                        st.markdown("---")

            with demographics_tab:
                st.subheader("Demographics Analysis")
                with st.spinner('Analyzing demographic data usage...'):
                    display_demographics_summary(demo_analyzer)
                    usage_summary = demo_analyzer.get_usage_summary()

                    if not usage_summary:
                        st.info("No demographic data usage found in the codebase")
                    else:
                        categories = list(usage_summary.keys())
                        category_tabs = st.tabs(categories)

                        for idx, category in enumerate(categories):
                            with category_tabs[idx]:
                                st.subheader(f"{category} Fields")

                                data = []
                                for usage in usage_summary[category]:
                                    data.append({
                                        'Field': usage.field_name,
                                        'File': usage.file_path,
                                        'Class': usage.class_name,
                                        'Method': usage.method_name,
                                        'Usage Type': usage.usage_type
                                    })

                                if data:
                                    df = pd.DataFrame(data)
                                    st.dataframe(df, hide_index=True)

                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        f"Download {category} Usage Data",
                                        csv,
                                        f"{category.lower()}_demographics.csv",
                                        "text/csv"
                                    )
                                else:
                                    st.info(f"No field usage found for {category}")

            with patterns_tab:
                st.subheader("Integration Patterns Analysis")
                analysis_type = st.radio(
                    "Select Analysis Type",
                    ["API Endpoints", "Service Dependencies", "Service Graph"]
                )
                with st.spinner('Analyzing microservices...'):
                    if analysis_type == "API Endpoints":
                        api_summary = ms_analyzer.get_api_summary()
                        for service, endpoints in api_summary.items():
                            with st.expander(f"Service: {service}", expanded=True):
                                for endpoint in endpoints:
                                    st.markdown(f"""
                                    **{endpoint['method']} {endpoint['path']}**
                                    Handler: `{endpoint['class']}.{endpoint['handler']}`
                                    """)

                    elif analysis_type == "Service Dependencies":
                        for dep in ms_analyzer.service_dependencies:
                            st.markdown(f"""
                            **{dep.source}** → **{dep.target}**
                            Type: {dep.type}
                            Details: {dep.details}
                            """)

                    elif analysis_type == "Service Graph":
                        with st.spinner('Generating service graph...'):
                            graph, graph_data = ms_analyzer.generate_service_graph()

                            fig, ax = plt.subplots(figsize=(12, 8))
                            pos = graph_data['positions']

                            nx.draw_networkx_nodes(graph, pos,
                                                    node_color='lightblue',
                                                    node_size=2000)

                            edge_colors = {'feign': 'blue', 'kafka': 'green', 'rest': 'red'}
                            for u, v, data in graph_data['edges']:
                                edge_type = data.get('type', 'rest')
                                nx.draw_networkx_edges(graph, pos,
                                                        edgelist=[(u, v)],
                                                        edge_color=edge_colors.get(edge_type, 'gray'))

                            nx.draw_networkx_labels(graph, pos)

                            buf = BytesIO()
                            plt.savefig(buf, format='png', bbox_inches='tight')
                            buf.seek(0)
                            plot_image = buf.getvalue()

                            st.download_button(
                                "Download Service Graph (PNG)",
                                plot_image,
                                "service_graph.png",
                                "image/png"
                            )

                            st.image(plot_image, caption="Service Dependency Graph", width=None)

                            st.markdown("""
                            **Legend:**
                            - Blue edges: Feign Client connections
                            - Green edges: Kafka connections
                            - Red edges: REST template calls
                            """)

            with db_tab:
                analyze_database_schema(java_files, project_path)

            with analysis_tab:
                st.subheader("Code Analysis Summary")
                patterns_col, demographics_col, integration_col = st.columns(3)

                with patterns_col:
                    st.markdown("### Design Patterns")
                    patterns = pattern_analyzer.get_patterns()
                    data = []
                    if patterns:
                        for pattern in patterns:
                            if isinstance(pattern, dict):
                                pattern_name = pattern.get('name', 'Unknown')
                                pattern_type = pattern.get('type', 'Unknown')
                                usage_count = pattern.get('usage_count', 0)
                                data.append({
                                    'Pattern Name': pattern_name,
                                    'Type': pattern_type,
                                    'Usage Count': usage_count
                                })
                            else:
                                st.warning(f"Invalid pattern data format: {pattern}")

                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.info("No specific patterns detected")

                with demographics_col:
                    st.markdown("### Demographic Data Usage")
                    usage_data = demo_analyzer.get_usage_summary()
                    if usage_data:
                        total_fields = sum(len(fields) for fields in usage_data.values())
                        st.metric("Total Demographic Fields", total_fields)

                        data = []
                        for category, fields in usage_data.items():
                            data.append({
                                'Category': category,
                                'Fields Count': len(fields),
                                'Fields': ', '.join([f.field_name for f in fields])
                            })
                        if data:
                            df = pd.DataFrame(data)
                            st.dataframe(df)
                    else:
                        st.info("No demographic data usage detected")

                with integration_col:
                    st.markdown("### Integration Patterns")
                    int_patterns = int_analyzer.get_patterns()
                    data = []
                    if int_patterns:
                        for pattern in int_patterns:
                            if isinstance(pattern, dict):
                                pattern_name = pattern.get('name', 'Unknown')
                                pattern_type = pattern.get('type', 'Unknown')
                                components = pattern.get('components', [])
                                data.append({
                                    'Pattern Name': pattern_name,
                                    'Type': pattern_type,
                                    'Components': ', '.join(components) if isinstance(components, list) else str(components)
                                })
                            else:
                                st.warning(f"Invalid pattern data format: {pattern}")

                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.info("No integration patterns detected")

        except Exception as e:
            handle_error(e)
            st.error(f"Error details: {str(e)}")
    else:
        st.info("Please upload a Java project (ZIP file) to begin analysis")


def display_project_structure(project_structure):
    st.subheader("Project Structure")

    if not project_structure:
        st.warning("No Java files found in the project")
        return

    data = []
    for package, files in project_structure.items():
        data.append({
            'Type': 'Package',
            'Name': package,
            'Path': '',
            'Classes': '',
            'Methods': '',
            'Description': f'Package containing {len(files)} files'
        })

        for file in files:
            class_names = [cls['name'] for cls in file['classes']]
            total_methods_in_file = sum(len(cls['methods']) for cls in file['classes'])
            data.append({
                'Type': 'File',
                'Name': os.path.basename(file['path']),
                'Path': file['path'],
                'Classes': ', '.join(class_names),
                'Methods': total_methods_in_file,
                'Description': file.get('description', '')
            })

    df = pd.DataFrame(data)

    st.dataframe(df,
        column_config={
            'Type': st.column_config.TextColumn(
                'Type',
                help='Package or File'
            ),
            'Name': st.column_config.TextColumn(
                'Name',
                help='Name of package or file'
            ),
            'Path': st.column_config.TextColumn(
                'Path',
                help='Full path of the file'
            ),
            'Classes': st.column_config.NumberColumn(
                'Classes',
                help='Number of classes in the file'
            ),
            'Methods': st.column_config.NumberColumn(
                'Methods',
                help='Number of methods across all classes'
            ),
            'Description': st.column_config.TextColumn(
                'Description',
                help='Additional information about the item'
            )
        },
        hide_index=True
    )

    st.subheader("Detailed Class View")

    selected_package = st.selectbox(
        "Select Package",
        options=list(project_structure.keys()),
        key="package_selector"
    )

    if selected_package:
        files = project_structure[selected_package]

        file_paths = [file['path'] for file in files]
        selected_file = st.selectbox(
            "Select a file to view details",
            sorted(file_paths)
        )

        if selected_file:
            file = next((f for f in files if f['path'] == selected_file), None)
            if file:
                st.markdown(f"### Classes in {os.path.basename(selected_file)}")

                if hasattr(file, 'classes'):
                    for class_info in file['classes']:
                        class_name = class_info['name'] if 'name' in class_info else 'Unknown Class'
                        with st.expander(f"📚 {class_name}"):
                            if 'extends' in class_info and class_info['extends']:
                                st.markdown(f"*Extends:* `{class_info['extends']}`")
                            if 'implements' in class_info and class_info['implements']:
                                st.markdown(f"*Implements:* `{', '.join(class_info['implements'])}`")

                            st.markdown("**Methods:**")
                            if 'methods' in class_info:
                                for method in class_info['methods']:
                                    if isinstance(method, str):
                                        st.markdown(f"- {method}")
                                    else:
                                        method_name = method['name'] if 'name' in method else 'Unknown Method'
                                        st.markdown(f"- {method_name}")

                            st.markdown("**Fields:**")
                            if 'fields' in class_info:
                                for field in class_info['fields']:
                                    if isinstance(field, str):
                                        st.markdown(f"- {field}")
                                    else:
                                        field_name = field['name'] if 'name' in field else 'Unknown Field'
                                        field_type = field['type'] if 'type' in field else 'Unknown Type'
                                        st.markdown(f"- {field_name}: {field_type}")
                else:
                    st.warning("No class information available for this file")


def display_code_structure(project_structure):
    st.subheader("Code Structure Analysis")

    if not project_structure:
        st.warning("No Java files found in the project")
        return

    selected_package = st.selectbox(
        "Select Package",
        options=list(project_structure.keys())
    )

    if selected_package:
        files = project_structure[selected_package]
        for file in files:
            with st.expander(f"File: {file['path']}", expanded=True):
                for class_info in file['classes']:
                    st.markdown(f"### Class: {class_info['name']}")
                    display_class_details(class_info)


def generate_project_uml(java_files):
    st.subheader("Project UML Class Diagram")

    if not java_files:
        st.warning("No Java files found to generate UML diagram")
        return

    with st.spinner('Generating UML diagram...'):
        uml_generator = UMLGenerator()
        all_classes = []

        for file in java_files:
            for class_info in file.classes:
                java_class = JavaClass.from_dict(class_info)
                all_classes.append(java_class)

        uml_code = uml_generator.generate_class_diagram(all_classes)
        st.text_area("PlantUML Code", uml_code, height=300)
        st.markdown(create_download_link(uml_code, "project_class_diagram.puml"), unsafe_allow_html=True)


def display_class_details(class_info):
    if 'extends' in class_info and class_info['extends']:
        st.markdown(f"**Extends:** {class_info['extends']}")

    if 'implements' in class_info and class_info['implements']:
        st.markdown(f"**Implements:**")
        for interface in class_info['implements']:
            st.markdown(f"- {interface}")

    st.markdown("**Fields:**")
    for field in class_info['fields']:
        st.markdown(f"- {field}")

    st.markdown("**Methods:**")
    for method in class_info['methods']:
        st.markdown(f"- {method}")


def generate_sequence_diagram(project_path):
    st.subheader("Sequence Diagram Generator")

    generator = SequenceDiagramGenerator()

    method_name = st.text_input("Enter method name to analyze:")
    if method_name:
        with st.spinner('Generating sequence diagram...'):
            sequence_diagram = generator.analyze_method_calls(project_path, method_name)
            st.text_area("PlantUML Sequence Diagram", sequence_diagram, height=300)
            st.markdown(create_download_link(sequence_diagram, "sequence_diagram.puml"), unsafe_allow_html=True)


def generate_call_graph(project_path):
    st.subheader("Function Call Graph")

    with st.spinner('Generating call graph...'):
        analyzer = CallGraphAnalyzer()
        graph = analyzer.analyze_calls(project_path)
        graph_data = analyzer.get_graph_data()

        fig, ax = plt.subplots(figsize=(10, 10))
        nx.draw(
            graph,
            pos=nx.spring_layout(graph),
            with_labels=True,
            node_color='lightblue',
            node_size=2000,
            font_size=8,
            font_weight='bold',
            arrows=True,
            ax=ax
        )
        st.pyplot(fig)


def analyze_database_schema(java_files, project_path):
    st.subheader("Legacy Database Analysis")

    analysis_type = st.radio(
        "Select Analysis Type",
        ["Legacy Systems Overview", "SQL Query Analysis"]
    )

    legacy_analyzer = LegacyTableAnalyzer()

    for file in java_files:
        file_path = os.path.join(project_path, file.path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                legacy_analyzer.analyze_code(file_path, code)
        except Exception as e:
            st.error(f"Error analyzing file {file_path}: {str(e)}")

    if analysis_type == "Legacy Systems Overview":
        usage_summary = legacy_analyzer.get_usage_summary()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Legacy Systems", len(usage_summary))
        with col2:
            total_tables = sum(len(tables) for tables in usage_summary.values())
            st.metric("Total Tables", total_tables)
        with col3:
            total_usages = sum(len(usages) for usages in usage_summary.values())
            st.metric("Total References", total_usages)

        if usage_summary:
            systems = list(usage_summary.keys())
            system_tabs = st.tabs(systems)

            for idx, system in enumerate(systems):
                with system_tabs[idx]:
                    st.subheader(f"{system} System Tables")

                    data = []
                    for usage in usage_summary[system]:
                        data.append({
                            'Table': usage.table_name,
                            'File': usage.file_path,
                            'Class': usage.class_name,
                            'Method': usage.method_name,
                            'Usage Type': usage.usage_type
                        })

                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df, hide_index=True)

                        csv = df.to_csv(index=False)
                        st.download_button(
                            f"Download {system} Usage Data",
                            csv,
                            f"{system.lower()}_table_usage.csv",
                            "text/csv"
                        )
                    else:
                        st.info(f"No table usage found for {system}")
        else:
            st.info("No legacy system usage found in the codebase")

    else:
        st.subheader("SQL Query Analysis")

        sql_types = {
            "SELECT": [],
            "INSERT": [],
            "UPDATE": [],
            "DELETE": []
        }

        for file in java_files:
            file_path = os.path.join(project_path, file.path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    for query_type in sql_types.keys():
                        pattern = rf'{query_type}\s+[^;]+;'
                        matches = re.finditer(pattern, code, re.IGNORECASE)
                        for match in matches:
                            sql_types[query_type].append({
                                'query': match.group(0),
                                'file': file.path
                            })
            except Exception as e:
                st.error(f"Error analyzing SQL in file {file_path}: {str(e)}")

        query_tabs = st.tabs(list(sql_types.keys()))

        for idx, (query_type, queries) in enumerate(sql_types.items()):
            with query_tabs[idx]:
                if queries:
                    for q in queries:
                        with st.expander(f"Query in {q['file']}", expanded=False):
                            st.code(q['query'], language='sql')
                else:
                    st.info(f"No {query_type} queries found")


def display_code_structure_summary(project_structure):
    col1,col2, col3 = st.columns(3)
    with col1:
        total_classes = sum(len(file['classes']) for files in project_structure.values() for file in files)
        st.metric("Total Classes", total_classes)
    with col2:
        total_methods = sum(len(class_info['methods']) for files in project_structure.values()
                            for file in files for class_info in file['classes'])
        st.metric("Total Methods", total_methods)
    with col3:
        total_fields = sum(len(class_info['fields']) for files in project_structure.values()
                            for file in files for class_info in file['classes'])
        st.metric("Total Fields", total_fields)


def display_diagrams_summary(java_files):
    total_classes = sum(1 for file in java_files for _ in file.classes)
    st.header(f"Class Diagram Analysis (Total Classes: {total_classes})")

    diagram_type = st.radio(
        "Select Diagram Type",
        ["UML Class Diagram"]
    )

    if diagram_type == "UML Class Diagram":
        with st.spinner('Generating class diagram...'):
            uml_generator = UMLGenerator()
            all_classes = []

            for file in java_files:
                for class_info in file.classes:
                    java_class = JavaClass.from_dict(class_info)
                    all_classes.append(java_class)

            section_size = 10
            class_sections = [all_classes[i:i + section_size]
                              for i in range(0, len(all_classes), section_size)]

            for i, section_classes in enumerate(class_sections, 1):
                with st.expander(f"Class Diagram Section {i} ({len(section_classes)} classes)", expanded=True):
                    uml_code, uml_image = uml_generator.generate_class_diagram(section_classes)

                    st.image(uml_image, caption=f"Class Diagram Section {i}", width=None)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label=f"📥 Download Section {i} (PNG)",
                            data=uml_image,
                            file_name=f"class_diagram_section_{i}.png",
                            mime="image/png",
                            help="Download this section of the UML diagram as a PNG image"
                        )
                    with col2:
                        st.download_button(
                            label=f"📄 Download PlantUML Code",
                            data=uml_code,
                            file_name=f"class_diagram_section_{i}.puml",
                            mime="text/plain",
                            help="Downloadthe PlantUML source code for this section"
                        )

                    with st.expander("View PlantUML Code"):
                        st.code(uml_code, language="text")


def display_legacysummary(legacy_analyzer):
    usage_summary = legacy_analyzer.get_usage_summary()
    col1, col2, col3 = st.columns(3)
    with col1:
        total_systems = len(usage_summary)
        st.metric("Legacy Systems",total_systems)
    with col2:
        total_tables = sum(len(tables) for tables in usage_summary.values())
        st.metric("Tables Referenced", total_tables)
    with col3:
        total_usages = sum(len(usage) for usage in usage_summary.values())
        st.metric("Total References", total_usages)


def display_demographics_summary(demo_analyzer):
    usage_summary = demo_analyzer.get_usage_summary()
    col1, col2, col3 = st.columns(3)
    with col1:
        total_categories = len(usage_summary)
        st.metric("Demographic Categories", total_categories)
    with col2:
        total_fields = sum(len(fields) for fields in usage_summary.values())
        st.metric("Fields Tracked", total_fields)
    with col3:
        total_usages = sum(len(usage) for usage in usage_summary.values())
        st.metric("Total References", total_usages)


def display_integration_summary(ms_analyzer):
    """Display integration summary in a table format"""
    api_summary = ms_analyzer.get_api_summary()
    col1, col2, col3 = st.columns(3)

    with col1:
        total_services = len(api_summary)
        st.metric("Microservices", total_services)

    with col2:
        total_endpoints = sum(len(endpoints) for endpoints in api_summary.values())
        st.metric("Total Endpoints", total_endpoints)

    with col3:
        total_controllers = sum(
            len([ep for ep in endpoints if 'handler' in ep and ep['handler']])
            for endpoints in api_summary.values()
        )
        st.metric("Total Controllers", total_controllers)


if __name__ == "__main__":
    main()