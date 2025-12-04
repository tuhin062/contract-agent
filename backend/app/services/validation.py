"""
Validation service for LLM-based contract analysis.
Provides risk scoring, clause detection, and compliance checking.
"""
from typing import Dict, List, Optional
import logging
from app.services.openrouter import openrouter_client

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating contracts using LLM analysis."""
    
    def __init__(self):
        """Initialize validation service."""
        self.llm = openrouter_client
    
    async def validate_contract(
        self,
        contract_text: str,
        contract_type: Optional[str] = None
    ) -> Dict:
        """
        Validate a contract using LLM analysis.
        
        Args:
            contract_text: Full contract text
            contract_type: Type of contract (e.g., "NDA", "Service Agreement")
            
        Returns:
            Validation report dictionary
        """
        # Build validation prompt
        prompt = self._build_validation_prompt(contract_text, contract_type)
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert legal contract analyst. Analyze contracts for risks, issues, and compliance."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            # Call LLM for analysis
            response = await self.llm.chat_completion(
                messages=messages,
                model="openai/gpt-4o",  # Use more powerful model for validation
                temperature=0.1  # Lower temperature for analytical tasks
            )
            
            analysis = response["choices"][0]["message"]["content"]
            
            # Parse LLM response into structured format
            report = self._parse_validation_response(analysis)
            
            # Calculate risk score
            risk_score, risk_level = self._calculate_risk_score(report)
            report["risk_score"] = risk_score
            report["risk_level"] = risk_level
            
            return report
            
        except Exception as e:
            logger.error(f"Contract validation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "suggestions": [],
                "risk_score": 0.5,
                "risk_level": "unknown"
            }
    
    def _build_validation_prompt(self, contract_text: str, contract_type: Optional[str]) -> str:
        """Build prompt for contract validation."""
        type_str = f"This is a {contract_type}." if contract_type else "Analyze this contract."
        
        prompt = f"""{type_str}

CONTRACT TEXT:
{contract_text[:4000]}  # Limit text to avoid token limits

ANALYSIS REQUIRED:
1. **Issues**: Identify potential problems, ambiguities, or risky clauses
2. **Suggestions**: Provide recommendations for improvements
3. **Key Clauses**: List important clauses found (e.g., termination, liability, confidentiality)
4. **Compliance**: Check for standard legal elements (parties, dates, signatures, etc.)

Provide your analysis in the following format:

ISSUES:
- [HIGH/MEDIUM/LOW] Issue description and location

SUGGESTIONS:
- Suggestion for improvement

KEY CLAUSES:
- Clause name: Description and location

COMPLIANCE:
- Element: Present/Missing

Be specific and reference locations in the contract when possible."""
        
        return prompt
    
    def _parse_validation_response(self, analysis: str) -> Dict:
        """
        Parse LLM response into structured format.
        
        This is a simplified parser. In production, you might use
        structured output or more sophisticated parsing.
        """
        report = {
            "issues": [],
            "suggestions": [],
            "clauses": [],
            "compliance": {},
            "raw_analysis": analysis
        }
        
        # Simple parsing logic
        sections = analysis.split("\n\n")
        current_section = None
        
        for section in sections:
            section = section.strip()
            if section.startswith("ISSUES"):
                current_section = "issues"
            elif section.startswith("SUGGESTIONS"):
                current_section = "suggestions"
            elif section.startswith("KEY CLAUSES"):
                current_section = "clauses"
            elif section.startswith("COMPLIANCE"):
                current_section = "compliance"
            elif current_section and section.startswith("-"):
                # Parse items
                item_text = section[1:].strip()
                
                if current_section == "issues":
                    # Extract severity
                    severity = "MEDIUM"
                    if "[HIGH]" in item_text:
                        severity = "HIGH"
                        item_text = item_text.replace("[HIGH]", "").strip()
                    elif "[LOW]" in item_text:
                        severity = "LOW"
                        item_text = item_text.replace("[LOW]", "").strip()
                    elif "[MEDIUM]" in item_text:
                        item_text = item_text.replace("[MEDIUM]", "").strip()
                    
                    report["issues"].append({
                        "severity": severity,
                        "message": item_text
                    })
                
                elif current_section == "suggestions":
                    report["suggestions"].append(item_text)
                
                elif current_section == "clauses":
                    if ":" in item_text:
                        clause_name, clause_desc = item_text.split(":", 1)
                        report["clauses"].append({
                            "name": clause_name.strip(),
                            "description": clause_desc.strip()
                        })
                
                elif current_section == "compliance":
                    if ":" in item_text:
                        element, status = item_text.split(":", 1)
                        report["compliance"][element.strip()] = status.strip()
        
        return report
    
    def _calculate_risk_score(self, report: Dict) -> tuple:
        """
        Calculate risk score from validation report.
        
        Returns:
            Tuple of (risk_score, risk_level)
        """
        # Count issues by severity
        high_issues = sum(1 for issue in report.get("issues", []) if issue.get("severity") == "HIGH")
        medium_issues = sum(1 for issue in report.get("issues", []) if issue.get("severity") == "MEDIUM")
        low_issues = sum(1 for issue in report.get("issues", []) if issue.get("severity") == "LOW")
        
        # Calculate weighted score (0.0 to 1.0, higher is riskier)
        risk_score = min(1.0, (high_issues * 0.3 + medium_issues * 0.15 + low_issues * 0.05))
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "CRITICAL"
        elif risk_score >= 0.5:
            risk_level = "HIGH"
        elif risk_score >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return risk_score, risk_level


# Global validation service instance
validation_service = ValidationService()
