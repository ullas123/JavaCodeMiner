import re
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class PatternMatch:
    pattern_type: str
    pattern_name: str
    file_path: str
    line_number: int
    matched_text: str

class IntegrationPatternAnalyzer:
    def __init__(self):
        self.integration_patterns = {
            'rest_api': {
                'http_methods': r'\b(get|post|put|delete|patch)\b.*\b(api|endpoint)\b',
                'url_patterns': r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                'api_endpoints': r'@RequestMapping|@GetMapping|@PostMapping|@PutMapping|@DeleteMapping'
            },
            'soap_services': {
                'soap_components': r'\b(soap|wsdl|xml)\b',
                'wsdl': r'wsdl|WSDL|\.wsdl|getWSDL|WebService[Client]?',
                'soap_operations': r'SOAPMessage|SOAPEnvelope|SOAPBody|SOAPHeader|SoapClient|SoapBinding',
                'xml_namespaces': r'xmlns[:=]|namespace|schemaLocation',
                'soap_annotations': r'@WebService|@WebMethod|@SOAPBinding|@WebResult|@WebParam',
                'soap_endpoints': r'endpoint[_\s]?url|service[_\s]?url|wsdl[_\s]?url'
            },
            'database': {
                'sql_operations': r'\b(select|insert|update|delete)\s+from|into\b',
                'db_connections': r'jdbc:|connection[_\s]?string|database[_\s]?url'
            },
            'messaging': {
                'kafka': r'kafka|producer|consumer|topic',
                'rabbitmq': r'rabbitmq|amqp',
                'jms': r'jms|queue|topic'
            },
            'file':{
                'file_operations': r'\b(csv|excel|xlsx|json|properties).*(read|write|load|save)\b'
            }
        }
        self.matches = []

    def analyze_code(self, file_path: str, content: str) -> None:
        """
        Analyze the given code content for integration patterns.
        This is the main entry point for code analysis.

        Args:
            file_path: Path to the file being analyzed
            content: The source code content to analyze
        """
        self.analyze_file(file_path, content)

    def analyze_file(self, file_path: str, content: str) -> None:
        lines = content.split('\n')
        for line_number, line in enumerate(lines, 1):
            for pattern_type, patterns in self.integration_patterns.items():
                for pattern_name, pattern in patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        self.matches.append(PatternMatch(
                            pattern_type=pattern_type,
                            pattern_name=pattern_name,
                            file_path=file_path,
                            line_number=line_number,
                            matched_text=match.group()
                        ))

    def get_pattern_summary(self) -> Dict[str, List[PatternMatch]]:
        summary = {}
        for match in self.matches:
            if match.pattern_type not in summary:
                summary[match.pattern_type] = []
            summary[match.pattern_type].append(match)
        return summary

    def get_statistics(self) -> Dict[str, int]:
        stats = {}
        for pattern_type in self.integration_patterns.keys():
            stats[pattern_type] = len([m for m in self.matches if m.pattern_type == pattern_type])
        return stats

    def get_patterns(self) -> Dict[str, List[PatternMatch]]:
        """
        Get all detected patterns grouped by type.
        This method is called by the main application to display results.

        Returns:
            Dict mapping pattern types to lists of matches
        """
        return self.get_pattern_summary()