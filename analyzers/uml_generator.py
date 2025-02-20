import os
from typing import List, Tuple
from .java_class import JavaClass
import subprocess
import tempfile
import logging

class UMLGenerator:
    def __init__(self):
        # Full path to PlantUML executable
        self.plantuml_cmd = "/nix/store/mpzhxv8sgnpp9v1zgljz64bviyqc39jj-plantuml-1.2024.4/bin/plantuml"

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
            # Create temporary directory for diagram files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write PlantUML code to a temporary file
                temp_puml = os.path.join(temp_dir, "diagram.puml")
                temp_png = os.path.join(temp_dir, "diagram.png")

                logging.info(f"Writing PlantUML code to {temp_puml}")
                with open(temp_puml, "w") as f:
                    f.write(diagram_code)

                # Generate PNG using local PlantUML command
                logging.info("Running PlantUML to generate diagram")
                result = subprocess.run(
                    [self.plantuml_cmd, "-tpng", temp_puml],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Check if PNG file was generated
                if not os.path.exists(temp_png):
                    logging.error("PlantUML output: " + result.stdout)
                    logging.error("PlantUML errors: " + result.stderr)
                    raise Exception("PlantUML failed to generate the diagram")

                # Read the generated PNG file
                logging.info(f"Reading generated PNG from {temp_png}")
                with open(temp_png, "rb") as f:
                    png_data = f.read()

                return diagram_code, png_data

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to run PlantUML: {str(e)}\nOutput: {e.output}")
        except Exception as e:
            raise Exception(f"Failed to generate diagram: {str(e)}")