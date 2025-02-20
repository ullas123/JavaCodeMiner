import javalang
from typing import List, Dict, Tuple
import os
import subprocess
import tempfile
import logging

class SequenceDiagramGenerator:
    def __init__(self):
        self.interactions = []
        self.current_class = None
        # Initialize local PlantUML setup
        self.plantuml_jar = os.path.join(os.getcwd(), "plantuml.jar")
        if not os.path.exists(self.plantuml_jar):
            logging.info("Downloading PlantUML jar...")
            # Download PlantUML jar if not present
            try:
                subprocess.run([
                    "curl", "-L", "-o", self.plantuml_jar,
                    "https://github.com/plantuml/plantuml/releases/download/v1.2024.0/plantuml-1.2024.0.jar"
                ], check=True)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to download PlantUML jar: {str(e)}")

    def analyze_method_calls(self, code: str, method_name: str) -> Tuple[str, bytes]:
        """Analyze method calls and generate sequence diagram."""
        try:
            tree = javalang.parse.parse(code)
            self.interactions = []
            self.current_class = None
            method_found = False

            # First pass: identify the class containing the target method
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                if not node.methods:
                    continue

                for method in node.methods:
                    if method.name == method_name:
                        self.current_class = node.name
                        self._analyze_method_body(method)
                        method_found = True
                        break
                if method_found:
                    break

            if not method_found:
                raise Exception(f"Method '{method_name}' not found in any class")

            diagram_code = self._generate_sequence_diagram()

            # Generate diagram using local PlantUML
            try:
                # Create temporary directory for diagram files
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Write PlantUML code to a temporary file
                    temp_puml = os.path.join(temp_dir, "sequence_diagram.puml")
                    temp_png = os.path.join(temp_dir, "sequence_diagram.png")

                    logging.info(f"Writing PlantUML code to {temp_puml}")
                    with open(temp_puml, "w") as f:
                        f.write(diagram_code)

                    # Generate PNG using local PlantUML jar
                    logging.info("Running PlantUML to generate diagram")
                    result = subprocess.run([
                        "java", "-jar", self.plantuml_jar,
                        "-tpng", temp_puml
                    ], capture_output=True, text=True, check=True)

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

        except javalang.parser.JavaSyntaxError as e:
            raise Exception(f"Java syntax error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to analyze method calls: {str(e)}")

    def _analyze_method_body(self, method_node):
        """Analyze method body for method calls."""
        if not method_node.body:
            return

        try:
            for path, node in method_node.filter(javalang.tree.MethodInvocation):
                if hasattr(node, 'qualifier') and node.qualifier:
                    # If we have a qualifier, use it as the target class
                    target_class = node.qualifier
                else:
                    # If no qualifier, the call is within the same class
                    target_class = self.current_class

                if hasattr(node, 'member'):
                    args = self._extract_arguments(node)
                    self.interactions.append({
                        'from': self.current_class,
                        'to': target_class,
                        'message': node.member,
                        'arguments': args
                    })
        except Exception as e:
            print(f"Warning: Could not analyze method body: {str(e)}")

    def _extract_arguments(self, method_node) -> List[str]:
        """Extract method call arguments."""
        args = []
        if hasattr(method_node, 'arguments'):
            for arg in method_node.arguments:
                if hasattr(arg, 'value'):
                    args.append(str(arg.value))
                elif hasattr(arg, 'member'):
                    args.append(str(arg.member))
                else:
                    args.append(str(arg))
        return args

    def _generate_sequence_diagram(self) -> str:
        """Generate PlantUML sequence diagram code."""
        if not self.interactions:
            raise Exception("No method interactions found to generate sequence diagram")

        diagram = [
            "@startuml",
            "skinparam sequenceMessageAlign center",
            "skinparam responseMessageBelowArrow true",
            "skinparam maxMessageSize 100",
            "skinparam sequence {",
            "    ArrowColor DeepSkyBlue",
            "    LifeLineBorderColor blue",
            "    ParticipantBorderColor DarkBlue",
            "    ParticipantBackgroundColor LightBlue",
            "    ParticipantFontStyle bold",
            "}"
        ]

        # Add participants
        participants = set()
        for interaction in self.interactions:
            participants.add(interaction['from'])
            participants.add(interaction['to'])

        for participant in sorted(participants):
            diagram.append(f'participant "{participant}" as {participant}')

        # Add interactions with arguments
        for interaction in self.interactions:
            args_str = f"({', '.join(interaction['arguments'])})" if interaction['arguments'] else ""
            diagram.append(
                f"{interaction['from']} -> {interaction['to']}: {interaction['message']}{args_str}"
            )

        diagram.append("@enduml")
        return "\n".join(diagram)