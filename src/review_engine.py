import logging
from typing import Dict, List
from .diff_parser import FileDiff, Hunk

logger = logging.getLogger(__name__)

class ReviewEngine:
    def __init__(self, openai_client):
        self.openai_client = openai_client

    def generate_review(self, diff: str) -> str:
        """Generate AI review from raw diff"""
        try:
            return self.openai_client.analyze_diff(diff)
        except Exception as e:
            logger.error(f"Review generation failed: {str(e)}")
            return "⚠️ AI review unavailable due to processing error"

    def parse_findings(self, analysis: str) -> List[Dict]:
        """Convert AI response to structured findings"""
        findings = []
        current_finding = {}

        for line in analysis.split('\n'):
            line = line.strip()
            if line.startswith('- ['):
                # New finding
                if current_finding:
                    findings.append(current_finding)
                parts = line[3:].split(']', 1)
                if len(parts) < 2:
                    continue  # Skip malformed lines
                    
                severity_category = parts[0].split(' ', 1)
                current_finding = {
                    'severity': severity_category[0],
                    'category': severity_category[1].strip(':') if len(severity_category) > 1 else "General",
                    'description': parts[1].strip(),
                    'impact': '',
                    'fix': ''
                }
            elif line.startswith('- Impact:'):
                if current_finding:
                    current_finding['impact'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Suggested fix:'):
                if current_finding:
                    current_finding['fix'] = line.split(':', 1)[1].strip()

        if current_finding:
            findings.append(current_finding)

        return findings