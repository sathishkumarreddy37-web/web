"""
Advanced Security Scanner - OWASP Top 10 & Beyond
Comprehensive security vulnerability detection for web applications
"""
import re
from typing import Dict, Any, List
from urllib.parse import urlparse, urljoin
from datetime import datetime


class SecurityScanner:
    """Advanced security vulnerability scanner"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.security_score = 100
        
    async def run_comprehensive_scan(
        self, 
        url: str, 
        page_content: str,
        response_headers: Dict[str, str],
        cookies: List[Dict[str, Any]],
        forms: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive security scan
        
        Args:
            url: Target URL
            page_content: HTML content
            response_headers: HTTP response headers
            cookies: Cookie information
            forms: Form elements found (optional)
            
        Returns:
            Security scan results
        """
        if forms is None:
            forms = []
            
        results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "checks_performed": [],
            "vulnerabilities": [],
            "security_score": 100,
            "risk_level": "LOW"
        }
        
        # 1. Security Headers Analysis
        header_vulns = self._check_security_headers(response_headers)
        results["checks_performed"].append("Security Headers")
        results["vulnerabilities"].extend(header_vulns)
        
        # 2. Cookie Security
        cookie_vulns = self._check_cookie_security(cookies)
        results["checks_performed"].append("Cookie Security")
        results["vulnerabilities"].extend(cookie_vulns)
        
        # 3. CSRF Protection
        csrf_vulns = self._check_csrf_protection(forms, page_content)
        results["checks_performed"].append("CSRF Protection")
        results["vulnerabilities"].extend(csrf_vulns)
        
        # 4. XSS Vulnerabilities
        xss_vulns = self._check_xss_vulnerabilities(forms, page_content)
        results["checks_performed"].append("XSS Prevention")
        results["vulnerabilities"].extend(xss_vulns)
        
        # 5. SQL Injection Detection
        sqli_vulns = self._check_sql_injection_vectors(forms)
        results["checks_performed"].append("SQL Injection")
        results["vulnerabilities"].extend(sqli_vulns)
        
        # 6. Sensitive Data Exposure
        data_vulns = self._check_sensitive_data_exposure(page_content, url)
        results["checks_performed"].append("Sensitive Data Exposure")
        results["vulnerabilities"].extend(data_vulns)
        
        # 7. HTTPS and TLS
        tls_vulns = self._check_tls_security(url, response_headers)
        results["checks_performed"].append("TLS/HTTPS")
        results["vulnerabilities"].extend(tls_vulns)
        
        # Calculate security score and totals
        results["security_score"] = self._calculate_security_score(results["vulnerabilities"])
        results["risk_level"] = self._determine_risk_level(results["security_score"], results["vulnerabilities"])
        results["total_vulnerabilities"] = len(results["vulnerabilities"])
        
        return results
    
    def _check_security_headers(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for missing or misconfigured security headers"""
        vulns = []
        
        # Critical security headers
        required_headers = {
            'content-security-policy': {
                'severity': 'HIGH',
                'owasp': 'A05:2021 – Security Misconfiguration',
                'description': 'Missing Content-Security-Policy header',
                'impact': 'Allows XSS attacks and data injection',
                'fix': "Add header: Content-Security-Policy: default-src 'self'"
            },
            'x-frame-options': {
                'severity': 'MEDIUM',
                'owasp': 'A05:2021 – Security Misconfiguration',
                'description': 'Missing X-Frame-Options header',
                'impact': 'Vulnerable to clickjacking attacks',
                'fix': 'Add header: X-Frame-Options: DENY or SAMEORIGIN'
            },
            'x-content-type-options': {
                'severity': 'MEDIUM',
                'owasp': 'A05:2021 – Security Misconfiguration',
                'description': 'Missing X-Content-Type-Options header',
                'impact': 'Vulnerable to MIME type sniffing',
                'fix': 'Add header: X-Content-Type-Options: nosniff'
            },
            'strict-transport-security': {
                'severity': 'HIGH',
                'owasp': 'A02:2021 – Cryptographic Failures',
                'description': 'Missing Strict-Transport-Security header',
                'impact': 'Vulnerable to man-in-the-middle attacks',
                'fix': 'Add header: Strict-Transport-Security: max-age=31536000; includeSubDomains'
            },
            'x-xss-protection': {
                'severity': 'MEDIUM',
                'owasp': 'A03:2021 – Injection',
                'description': 'Missing X-XSS-Protection header',
                'impact': 'No XSS filter in older browsers',
                'fix': 'Add header: X-XSS-Protection: 1; mode=block'
            },
            'referrer-policy': {
                'severity': 'LOW',
                'owasp': 'A01:2021 – Broken Access Control',
                'description': 'Missing Referrer-Policy header',
                'impact': 'May leak sensitive URL information',
                'fix': 'Add header: Referrer-Policy: no-referrer or strict-origin-when-cross-origin'
            },
            'permissions-policy': {
                'severity': 'LOW',
                'owasp': 'A05:2021 – Security Misconfiguration',
                'description': 'Missing Permissions-Policy header',
                'impact': 'No control over browser features',
                'fix': 'Add header: Permissions-Policy: geolocation=(), microphone=()'
            }
        }
        
        # Check each header
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        for header, info in required_headers.items():
            if header not in headers_lower:
                vulns.append({
                    "type": "Missing Security Header",
                    "header": header,
                    "severity": info['severity'],
                    "owasp_category": info['owasp'],
                    "description": info['description'],
                    "impact": info['impact'],
                    "fix": info['fix'],
                    "cvss_score": self._severity_to_cvss(info['severity'])
                })
        
        return vulns
    
    def _check_cookie_security(self, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check cookie security attributes"""
        vulns = []
        
        for cookie in cookies:
            name = cookie.get('name', 'unknown')
            
            # Check Secure flag
            if not cookie.get('secure', False):
                vulns.append({
                    "type": "Insecure Cookie",
                    "cookie": name,
                    "severity": "HIGH",
                    "owasp_category": "A02:2021 – Cryptographic Failures",
                    "description": f"Cookie '{name}' missing Secure flag",
                    "impact": "Cookie can be transmitted over unencrypted connections",
                    "fix": "Set Secure attribute: Set-Cookie: name=value; Secure",
                    "cvss_score": 7.5
                })
            
            # Check HttpOnly flag
            if not cookie.get('httpOnly', False):
                vulns.append({
                    "type": "Cookie Accessible to JavaScript",
                    "cookie": name,
                    "severity": "MEDIUM",
                    "owasp_category": "A03:2021 – Injection",
                    "description": f"Cookie '{name}' missing HttpOnly flag",
                    "impact": "Cookie accessible via JavaScript, vulnerable to XSS",
                    "fix": "Set HttpOnly attribute: Set-Cookie: name=value; HttpOnly",
                    "cvss_score": 5.3
                })
            
            # Check SameSite attribute
            if not cookie.get('sameSite'):
                vulns.append({
                    "type": "CSRF Vulnerable Cookie",
                    "cookie": name,
                    "severity": "MEDIUM",
                    "owasp_category": "A01:2021 – Broken Access Control",
                    "description": f"Cookie '{name}' missing SameSite attribute",
                    "impact": "Vulnerable to CSRF attacks",
                    "fix": "Set SameSite attribute: Set-Cookie: name=value; SameSite=Strict",
                    "cvss_score": 6.1
                })
        
        return vulns
    
    def _check_csrf_protection(self, forms: List[Dict[str, Any]], page_content: str) -> List[Dict[str, Any]]:
        """Check for CSRF token protection"""
        vulns = []
        
        # Common CSRF token patterns
        csrf_patterns = [
            r'csrf[_-]?token',
            r'csrfmiddlewaretoken',
            r'_token',
            r'authenticity_token',
            r'__requestverificationtoken'
        ]
        
        for form in forms:
            has_csrf_token = False
            
            # Check if form has CSRF token
            for pattern in csrf_patterns:
                if re.search(pattern, page_content, re.IGNORECASE):
                    has_csrf_token = True
                    break
            
            if not has_csrf_token:
                method = form.get('method', 'GET').upper()
                if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    vulns.append({
                        "type": "Missing CSRF Protection",
                        "severity": "HIGH",
                        "owasp_category": "A01:2021 – Broken Access Control",
                        "description": f"Form with {method} method lacks CSRF token",
                        "impact": "Application vulnerable to Cross-Site Request Forgery",
                        "fix": "Implement CSRF tokens for all state-changing operations",
                        "cvss_score": 8.1
                    })
        
        return vulns
    
    def _check_xss_vulnerabilities(self, forms: List[Dict[str, Any]], page_content: str) -> List[Dict[str, Any]]:
        """Check for XSS vulnerability indicators"""
        vulns = []
        
        # Check for unescaped user input patterns
        xss_indicators = [
            (r'<script[^>]*>[^<]*</script>', 'Inline JavaScript'),
            (r'on\w+\s*=\s*["\'][^"\']*["\']', 'Event handlers'),
            (r'javascript:', 'JavaScript protocol'),
        ]
        
        for pattern, desc in xss_indicators:
            if re.search(pattern, page_content, re.IGNORECASE):
                vulns.append({
                    "type": "Potential XSS Vulnerability",
                    "indicator": desc,
                    "severity": "HIGH",
                    "owasp_category": "A03:2021 – Injection",
                    "description": f"Found {desc} in page content",
                    "impact": "May allow Cross-Site Scripting attacks",
                    "fix": "Sanitize and encode all user inputs before rendering",
                    "cvss_score": 7.3
                })
        
        # Check forms for input validation
        for form in forms:
            inputs = form.get('inputs', [])
            for inp in inputs:
                input_type = inp.get('type', 'text')
                if input_type in ['text', 'email', 'search']:
                    vulns.append({
                        "type": "Unvalidated Input Field",
                        "severity": "MEDIUM",
                        "owasp_category": "A03:2021 – Injection",
                        "description": f"Input field lacks client-side validation",
                        "impact": "May accept malicious input",
                        "fix": "Add input validation and sanitization",
                        "cvss_score": 5.4
                    })
                    break  # Report once per form
        
        return vulns
    
    def _check_sql_injection_vectors(self, forms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for SQL injection vulnerability indicators"""
        vulns = []
        
        for form in forms:
            action = form.get('action', '')
            method = form.get('method', 'GET').upper()
            
            # Check for suspicious query parameters
            if '?' in action or method == 'GET':
                vulns.append({
                    "type": "Potential SQL Injection Vector",
                    "severity": "CRITICAL",
                    "owasp_category": "A03:2021 – Injection",
                    "description": "Form uses GET method or query parameters",
                    "impact": "May be vulnerable to SQL injection if inputs not parameterized",
                    "fix": "Use POST method and parameterized queries/prepared statements",
                    "cvss_score": 9.8
                })
                break  # Report once
        
        return vulns
    
    def _check_sensitive_data_exposure(self, page_content: str, url: str) -> List[Dict[str, Any]]:
        """Check for sensitive data exposure"""
        vulns = []
        
        # Patterns for sensitive data
        sensitive_patterns = {
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': 'Email addresses',
            r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b': 'Social Security Numbers',
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b': 'Credit card numbers',
            r'\b(?:password|passwd|pwd)\s*[:=]\s*[\'"]?[\w@#$%^&*]+[\'"]?': 'Hardcoded passwords',
            r'api[_-]?key\s*[:=]\s*[\'"]?[\w-]+[\'"]?': 'API keys',
            r'(?:secret|token)\s*[:=]\s*[\'"]?[\w-]+[\'"]?': 'Secret tokens'
        }
        
        for pattern, data_type in sensitive_patterns.items():
            matches = re.findall(pattern, page_content, re.IGNORECASE)
            if matches:
                vulns.append({
                    "type": "Sensitive Data Exposure",
                    "data_type": data_type,
                    "severity": "CRITICAL",
                    "owasp_category": "A02:2021 – Cryptographic Failures",
                    "description": f"Found {data_type} in page source",
                    "impact": "Sensitive information exposed to users",
                    "fix": "Remove sensitive data from client-side code",
                    "cvss_score": 9.1
                })
        
        return vulns
    
    def _check_tls_security(self, url: str, headers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check TLS/HTTPS configuration"""
        vulns = []
        
        parsed = urlparse(url)
        
        # Check if HTTPS
        if parsed.scheme != 'https':
            vulns.append({
                "type": "No HTTPS",
                "severity": "CRITICAL",
                "owasp_category": "A02:2021 – Cryptographic Failures",
                "description": "Website not using HTTPS",
                "impact": "All data transmitted in clear text",
                "fix": "Implement HTTPS with valid SSL/TLS certificate",
                "cvss_score": 9.3
            })
        
        return vulns
    
    def _calculate_security_score(self, vulnerabilities: List[Dict[str, Any]]) -> int:
        """Calculate overall security score (0-100)"""
        if not vulnerabilities:
            return 100
        
        # Deduct points based on severity
        severity_deductions = {
            'CRITICAL': 25,
            'HIGH': 15,
            'MEDIUM': 8,
            'LOW': 3
        }
        
        score = 100
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'LOW')
            score -= severity_deductions.get(severity, 5)
        
        return max(0, score)
    
    def _determine_risk_level(self, score: int, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Determine overall risk level"""
        # Check for critical vulnerabilities
        has_critical = any(v.get('severity') == 'CRITICAL' for v in vulnerabilities)
        if has_critical:
            return "CRITICAL"
        
        # Check by score
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _severity_to_cvss(self, severity: str) -> float:
        """Convert severity to CVSS score"""
        mapping = {
            'CRITICAL': 9.0,
            'HIGH': 7.5,
            'MEDIUM': 5.5,
            'LOW': 3.0
        }
        return mapping.get(severity, 5.0)
