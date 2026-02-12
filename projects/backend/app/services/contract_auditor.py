"""
Smart Contract Auditor Service for Algorand.

Analyzes TEAL code and Algorand Python contracts for security vulnerabilities,
optimization opportunities, and best practices compliance.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.config import settings

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    """Severity levels for audit findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(str, Enum):
    """Types of audit findings."""
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    BEST_PRACTICE = "best_practice"
    GAS = "gas"
    LOGIC = "logic"
    INFO = "info"


@dataclass
class AuditFinding:
    """Represents a single audit finding."""
    type: FindingType
    severity: SeverityLevel
    title: str
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class ContractAuditResult:
    """Result of a smart contract audit."""
    risk_score: int  # 0-100
    findings: List[AuditFinding]
    summary: str
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    lines_analyzed: int
    analysis_time_ms: float


class ContractAuditor:
    """
    AI-powered smart contract auditor for Algorand.
    
    Analyzes TEAL bytecode and Algorand Python (PyTeal) contracts
    for security vulnerabilities and optimization opportunities.
    """
    
    # TEAL opcodes that are potentially dangerous
    DANGEROUS_OPCODES = [
        "callsub", "retsub",  # Control flow
        "b", "bz", "bnz",  # Branching
        "loop",  # Loops
        "pop",  # Stack manipulation
    ]
    
    # Patterns that indicate potential vulnerabilities
    VULNERABILITY_PATTERNS = {
        "reentrancy": [
            r"callsub.*pop",  # External call followed by state change
            r"app_global_put.*callsub",  # State change before external call
        ],
        "integer_overflow": [
            r"\+\s*$",  # Addition without bounds check
            r"\*\s*$",  # Multiplication without bounds check
        ],
        "unprotected_access": [
            r"app_global_put(?!.+Txn\.Sender)",  # Global state write without sender check
            r"app_local_put(?!.+Txn\.Sender)",  # Local state write without sender check
        ],
        "front_running": [
            r"global\s+GroupSize",  # Group size checks
            r"TxnApplicationID",  # Application ID checks
        ],
        "unbounded_loop": [
            r"loop(?!.+pop)",  # Loop without exit condition
        ],
    }
    
    # Best practice patterns
    BEST_PRACTICE_PATTERNS = {
        "missing_version": r"^#pragma version",
        "missing_approval": r"approval_program",
        "missing_clear": r"clear_state_program",
    }
    
    def __init__(self) -> None:
        """Initialize the contract auditor."""
        self.ai_model = settings.AI_MODEL
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
    
    async def audit_contract(
        self,
        code: str,
        language: str = "teal",
        check_types: Optional[List[str]] = None
    ) -> ContractAuditResult:
        """
        Audit a smart contract for vulnerabilities and issues.
        
        Args:
            code: The contract source code
            language: The contract language (teal, python, pyteal)
            check_types: Types of checks to perform (security, optimization, best_practice)
        
        Returns:
            ContractAuditResult with findings and risk score
        """
        import time
        start_time = time.time()
        
        if check_types is None:
            check_types = ["security", "optimization", "best_practice"]
        
        findings: List[AuditFinding] = []
        lines = code.split('\n')
        
        # Perform static analysis
        if language.lower() == "teal":
            findings.extend(self._analyze_teal(code, lines, check_types))
        elif language.lower() in ["python", "pyteal"]:
            findings.extend(self._analyze_python(code, lines, check_types))
        
        # Perform AI-powered deep analysis
        ai_findings = await self._ai_deep_analysis(code, language, check_types)
        findings.extend(ai_findings)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(findings)
        
        # Generate summary
        summary = self._generate_summary(findings, risk_score)
        
        analysis_time = (time.time() - start_time) * 1000
        
        return ContractAuditResult(
            risk_score=risk_score,
            findings=findings,
            summary=summary,
            total_issues=len(findings),
            critical_count=sum(1 for f in findings if f.severity == SeverityLevel.CRITICAL),
            high_count=sum(1 for f in findings if f.severity == SeverityLevel.HIGH),
            medium_count=sum(1 for f in findings if f.severity == SeverityLevel.MEDIUM),
            low_count=sum(1 for f in findings if f.severity == SeverityLevel.LOW),
            lines_analyzed=len(lines),
            analysis_time_ms=analysis_time
        )
    
    def _analyze_teal(
        self,
        code: str,
        lines: List[str],
        check_types: List[str]
    ) -> List[AuditFinding]:
        """Perform static analysis on TEAL code."""
        findings: List[AuditFinding] = []
        
        # Check for version pragma
        if not re.search(r"^#pragma version", code, re.MULTILINE):
            findings.append(AuditFinding(
                type=FindingType.BEST_PRACTICE,
                severity=SeverityLevel.MEDIUM,
                title="Missing Version Pragma",
                description="Contract does not specify TEAL version pragma. This may cause compatibility issues.",
                recommendation="Add '#pragma version X' at the top of your contract (X >= 8 recommended)",
                references=["https://developer.algorand.org/docs/get-details/dapps/avm/teal/"]
            ))
        
        # Check for security vulnerabilities
        if "security" in check_types:
            for vuln_type, patterns in self.VULNERABILITY_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = code[:match.start()].count('\n') + 1
                        findings.append(self._create_vulnerability_finding(
                            vuln_type, line_num, lines[line_num - 1] if line_num <= len(lines) else ""
                        ))
        
        # Check for unprotected state access
        if "security" in check_types:
            if re.search(r"app_global_put", code) and not re.search(r"Txn\.Sender", code):
                findings.append(AuditFinding(
                    type=FindingType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    title="Unprotected Global State Write",
                    description="Global state is written without sender verification. Anyone could modify contract state.",
                    recommendation="Add sender check: 'Txn.Sender' before state modifications",
                    references=["https://developer.algorand.org/docs/get-details/dapps/smart-contracts/apps/"]
                ))
        
        # Check for optimization opportunities
        if "optimization" in check_types:
            # Check for repeated computations
            if code.count("balance") > 2:
                findings.append(AuditFinding(
                    type=FindingType.OPTIMIZATION,
                    severity=SeverityLevel.LOW,
                    title="Repeated Balance Checks",
                    description="Multiple balance checks detected. Consider caching the result.",
                    recommendation="Store balance in scratch space and reuse"
                ))
            
            # Check for excessive byte copying
            if code.count("dup") > 5:
                findings.append(AuditFinding(
                    type=FindingType.OPTIMIZATION,
                    severity=SeverityLevel.LOW,
                    title="Excessive Stack Duplication",
                    description="Many 'dup' operations detected. This may indicate inefficient stack management.",
                    recommendation="Review stack management to reduce duplication"
                ))
        
        # Check for best practices
        if "best_practice" in check_types:
            # Check for error handling
            if "err" not in code.lower() and "assert" not in code.lower():
                findings.append(AuditFinding(
                    type=FindingType.BEST_PRACTICE,
                    severity=SeverityLevel.MEDIUM,
                    title="Missing Error Handling",
                    description="No error handling or assertions found in the contract.",
                    recommendation="Add 'assert' or 'err' for proper error handling"
                ))
            
            # Check for comments
            comment_lines = sum(1 for line in lines if line.strip().startswith('//'))
            if comment_lines < len(lines) * 0.1:
                findings.append(AuditFinding(
                    type=FindingType.BEST_PRACTICE,
                    severity=SeverityLevel.INFO,
                    title="Insufficient Documentation",
                    description=f"Only {comment_lines} comment lines found in {len(lines)} lines of code.",
                    recommendation="Add more comments to explain contract logic"
                ))
        
        return findings
    
    def _analyze_python(
        self,
        code: str,
        lines: List[str],
        check_types: List[str]
    ) -> List[AuditFinding]:
        """Perform static analysis on Python/PyTeal code."""
        findings: List[AuditFinding] = []
        
        # Check for imports
        if "pyteal" not in code.lower() and "algopy" not in code.lower():
            findings.append(AuditFinding(
                type=FindingType.BEST_PRACTICE,
                severity=SeverityLevel.LOW,
                title="Unknown Framework",
                description="Code doesn't appear to use PyTeal or AlgoPy frameworks.",
                recommendation="Consider using PyTeal or algopy for safer contract development"
            ))
        
        # Check for security issues
        if "security" in check_types:
            # Check for hardcoded values
            if re.search(r'=\s*["\'][a-zA-Z0-9]{40,}["\']', code):
                findings.append(AuditFinding(
                    type=FindingType.SECURITY,
                    severity=SeverityLevel.MEDIUM,
                    title="Potential Hardcoded Secret",
                    description="Found what appears to be a hardcoded secret or address.",
                    recommendation="Use environment variables or parameters instead of hardcoded values"
                ))
            
            # Check for unsafe randomness
            if "random" in code.lower() and "VRF" not in code:
                findings.append(AuditFinding(
                    type=FindingType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    title="Potentially Unsafe Randomness",
                    description="Random function detected without VRF. On-chain randomness may be predictable.",
                    recommendation="Use Algorand VRF for secure randomness"
                ))
        
        # Check for best practices
        if "best_practice" in check_types:
            # Check for type hints
            if ":" not in code or "->" not in code:
                findings.append(AuditFinding(
                    type=FindingType.BEST_PRACTICE,
                    severity=SeverityLevel.INFO,
                    title="Missing Type Hints",
                    description="No type hints found in Python code.",
                    recommendation="Add type hints for better code documentation and IDE support"
                ))
            
            # Check for docstrings
            if '"""' not in code and "'''" not in code:
                findings.append(AuditFinding(
                    type=FindingType.BEST_PRACTICE,
                    severity=SeverityLevel.INFO,
                    title="Missing Docstrings",
                    description="No docstrings found in Python code.",
                    recommendation="Add docstrings to document functions and classes"
                ))
        
        return findings
    
    async def _ai_deep_analysis(
        self,
        code: str,
        language: str,
        check_types: List[str]
    ) -> List[AuditFinding]:
        """Use AI to perform deep analysis of the contract."""
        findings: List[AuditFinding] = []
        
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not configured, skipping AI analysis")
            return findings
        
        try:
            import httpx
            
            prompt = f"""You are a smart contract security auditor specializing in Algorand blockchain. 
Analyze the following {language.upper()} smart contract code for security vulnerabilities, 
optimization opportunities, and best practice violations.

Contract Code:
```
{code[:3000]}  # Limit code length for API
```

Focus on these check types: {', '.join(check_types)}

Provide your analysis as a JSON array of findings:
[
    {{
        "type": "security|optimization|best_practice",
        "severity": "critical|high|medium|low|info",
        "title": "Brief title",
        "description": "Detailed description",
        "recommendation": "How to fix"
    }}
]

Return ONLY the JSON array, no additional text."""

            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://chainguardian.app",
                "X-Title": "ChainGuardian Contract Auditor",
            }
            
            payload = {
                "model": self.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a smart contract security auditor. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            ai_findings = json.loads(content)
            
            # Parse AI findings
            if isinstance(ai_findings, dict) and "findings" in ai_findings:
                ai_findings = ai_findings["findings"]
            
            for finding in ai_findings if isinstance(ai_findings, list) else []:
                try:
                    findings.append(AuditFinding(
                        type=FindingType(finding.get("type", "security")),
                        severity=SeverityLevel(finding.get("severity", "medium")),
                        title=finding.get("title", "AI Finding"),
                        description=finding.get("description", ""),
                        recommendation=finding.get("recommendation", "")
                    ))
                except ValueError:
                    # Skip invalid finding types/severities
                    continue
                    
        except Exception as e:
            logger.error(f"AI deep analysis failed: {e}")
            # Add a note about AI analysis failure
            findings.append(AuditFinding(
                type=FindingType.INFO,
                severity=SeverityLevel.INFO,
                title="AI Analysis Unavailable",
                description=f"AI-powered deep analysis could not be completed: {str(e)[:100]}",
                recommendation="Check API configuration and try again"
            ))
        
        return findings
    
    def _create_vulnerability_finding(
        self,
        vuln_type: str,
        line_num: int,
        code_snippet: str
    ) -> AuditFinding:
        """Create a finding for a detected vulnerability."""
        vuln_info = {
            "reentrancy": {
                "severity": SeverityLevel.CRITICAL,
                "title": "Potential Reentrancy Vulnerability",
                "description": "State changes after external calls may allow reentrancy attacks.",
                "recommendation": "Follow checks-effects-interactions pattern"
            },
            "integer_overflow": {
                "severity": SeverityLevel.HIGH,
                "title": "Potential Integer Overflow",
                "description": "Arithmetic operations without bounds checking.",
                "recommendation": "Add bounds checks before arithmetic operations"
            },
            "unprotected_access": {
                "severity": SeverityLevel.HIGH,
                "title": "Unprotected State Access",
                "description": "State can be modified without proper access control.",
                "recommendation": "Add sender verification before state modifications"
            },
            "front_running": {
                "severity": SeverityLevel.MEDIUM,
                "title": "Potential Front-Running Vulnerability",
                "description": "Transaction ordering may be exploitable.",
                "recommendation": "Consider using commit-reveal schemes"
            },
            "unbounded_loop": {
                "severity": SeverityLevel.HIGH,
                "title": "Unbounded Loop",
                "description": "Loop without clear exit condition may cause out-of-gas.",
                "recommendation": "Add explicit loop bounds"
            }
        }
        
        info = vuln_info.get(vuln_type, {
            "severity": SeverityLevel.MEDIUM,
            "title": f"Potential {vuln_type.replace('_', ' ').title()}",
            "description": f"Potential {vuln_type} vulnerability detected.",
            "recommendation": "Review and fix the identified issue"
        })
        
        return AuditFinding(
            type=FindingType.SECURITY,
            severity=info["severity"],
            title=info["title"],
            description=info["description"],
            line_number=line_num,
            code_snippet=code_snippet,
            recommendation=info["recommendation"]
        )
    
    def _calculate_risk_score(self, findings: List[AuditFinding]) -> int:
        """Calculate overall risk score based on findings."""
        if not findings:
            return 0
        
        score = 0
        weights = {
            SeverityLevel.CRITICAL: 40,
            SeverityLevel.HIGH: 25,
            SeverityLevel.MEDIUM: 15,
            SeverityLevel.LOW: 5,
            SeverityLevel.INFO: 0
        }
        
        for finding in findings:
            score += weights.get(finding.severity, 0)
        
        # Cap at 100
        return min(100, score)
    
    def _generate_summary(self, findings: List[AuditFinding], risk_score: int) -> str:
        """Generate a human-readable summary of the audit."""
        if not findings:
            return "No issues found. Contract appears to be well-written."
        
        critical = sum(1 for f in findings if f.severity == SeverityLevel.CRITICAL)
        high = sum(1 for f in findings if f.severity == SeverityLevel.HIGH)
        medium = sum(1 for f in findings if f.severity == SeverityLevel.MEDIUM)
        low = sum(1 for f in findings if f.severity == SeverityLevel.LOW)
        
        risk_level = "LOW"
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        
        summary = f"Risk Level: {risk_level} (Score: {risk_score}/100)\n"
        summary += f"Issues Found: {critical} critical, {high} high, {medium} medium, {low} low\n"
        
        if critical > 0:
            summary += "\n⚠️ CRITICAL: This contract has critical vulnerabilities and should not be deployed!"
        elif high > 0:
            summary += "\n⚠️ WARNING: This contract has high-severity issues that should be addressed before deployment."
        elif medium > 0:
            summary += "\nℹ️ NOTICE: This contract has medium-severity issues that should be reviewed."
        else:
            summary += "\n✅ Contract appears relatively safe, but review all findings before deployment."
        
        return summary


# Singleton instance
_contract_auditor: Optional[ContractAuditor] = None


def get_contract_auditor() -> ContractAuditor:
    """Get or create the contract auditor singleton instance."""
    global _contract_auditor
    if _contract_auditor is None:
        _contract_auditor = ContractAuditor()
    return _contract_auditor
