import os
from typing import List, Tuple
from .java_class import JavaClass
import subprocess
import base64

class UMLGenerator:
    def __init__(self):
        # Initialize local PlantUML setup
        self.plantuml_jar = "plantuml.jar"  # PlantUML jar will be in the project root
        if not os.path.exists(self.plantuml_jar):
            # Download PlantUML jar if not present
            subprocess.run([
                "curl", "-L", "-o", self.plantuml_jar,
                "https://github.com/plantuml/plantuml/releases/download/v1.2024.0/plantuml-1.2024.0.jar"
            ])

    def generate_class_diagram(self, classes: List[JavaClass]) -> Tuple[str, bytes]:
        """Generate class diagram and return both PlantUML code and PNG image"""
        uml_code = [
            "@startuml",
            "' Modern style configuration",
            "skinparam monochrome false",
            "skinparam shadowing false",
            "skinparam classAttributeIconSize 0",
            "skinparam classFontStyle bold",
            "skinparam classBackgroundColor LightBlue",
            "skinparam classBorderColor DarkBlue",
            "skinparam packageBackgroundColor White",
            "skinparam stereotypeCBackgroundColor LightYellow",
            "skinparam interfaceBackgroundColor LightGreen",

            "' Layout configuration",
            "skinparam linetype ortho",
            "left to right direction",

            "' Add title and header",
            "title Java Project Class Diagram\n",
            "header Generated by CodeMXJ\n",
            "footer Page %page% of %lastpage%"
        ]

        # Group classes by package
        packages = {}
        for java_class in classes:
            package = java_class.package if hasattr(java_class, 'package') else 'default'
            if package not in packages:
                packages[package] = []
            packages[package].append(java_class)

        # Generate package and class definitions
        for package, pkg_classes in packages.items():
            if package != 'default':
                uml_code.append(f"\npackage {package} {{")

            for java_class in pkg_classes:
                # Add class stereotypes
                stereotypes = []
                if hasattr(java_class, 'is_interface') and java_class.is_interface:
                    stereotypes.append("interface")
                if hasattr(java_class, 'is_abstract') and java_class.is_abstract:
                    stereotypes.append("abstract")

                stereotype_str = f" <<{','.join(stereotypes)}>>" if stereotypes else ""
                uml_code.append(f"\nclass {java_class.name}{stereotype_str} {{")

                # Add fields with visibility
                if java_class.fields:
                    for field in java_class.fields:
                        visibility = '+' if 'public' in field.lower() else '-'
                        uml_code.append(f"  {visibility}{field}")

                # Add methods with visibility
                if java_class.methods:
                    uml_code.append("")  # Add spacing between fields and methods
                    for method in java_class.methods:
                        visibility = '+' if 'public' in method.lower() else '-'
                        uml_code.append(f"  {visibility}{method}")

                uml_code.append("}")

                # Add class notes if available
                if hasattr(java_class, 'description') and java_class.description:
                    uml_code.append(f"note right of {java_class.name}")
                    uml_code.append(f"  {java_class.description}")
                    uml_code.append("end note")

            if package != 'default':
                uml_code.append("}")

        # Add relationships
        for java_class in classes:
            # Inheritance
            if java_class.extends:
                uml_code.append(f"{java_class.name} --|> {java_class.extends}")

            # Implementations
            if java_class.implements:
                for interface in java_class.implements:
                    uml_code.append(f"{java_class.name} ..|> {interface}")

        uml_code.append("@enduml")
        diagram_code = "\n".join(uml_code)

        # Generate diagram using local PlantUML
        try:
            # Write PlantUML code to a temporary file
            temp_puml = "temp_diagram.puml"
            with open(temp_puml, "w") as f:
                f.write(diagram_code)

            # Generate PNG using local PlantUML jar
            subprocess.run([
                "java", "-jar", self.plantuml_jar,
                "-tpng", temp_puml
            ])

            # Read the generated PNG file
            png_file = "temp_diagram.png"
            with open(png_file, "rb") as f:
                png_data = f.read()

            # Clean up temporary files
            os.remove(temp_puml)
            os.remove(png_file)

            return diagram_code, png_data
        except Exception as e:
            raise Exception(f"Failed to generate diagram: {str(e)}")