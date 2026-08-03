"""
AI-Powered Accessibility Analyzer
WCAG 2.1 Level AA/AAA compliance checker with AI recommendations
"""
import re
from typing import Dict, Any, List
from datetime import datetime


class AccessibilityAnalyzer:
    """Comprehensive WCAG 2.1 accessibility analysis"""
    
    def __init__(self):
        self.wcag_level = "AA"  # Can be A, AA, or AAA
        self.issues = []
        
    async def analyze_accessibility(
        self,
        page_content: str,
        page_title: str,
        images: List[Dict[str, Any]],
        forms: List[Dict[str, Any]],
        headings: List[str]
    ) -> Dict[str, Any]:
        """
        Comprehensive accessibility analysis
        
        Args:
            page_content: HTML content
            page_title: Page title
            images: List of images found
            forms: List of forms found
            headings: List of headings (h1-h6)
            
        Returns:
            Accessibility analysis results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "wcag_level": self.wcag_level,
            "compliance_score": 100,
            "issues": [],
            "recommendations": [],
            "affected_users": []
        }
        
        # 1. Perceivable (WCAG Principle 1)
        perceivable_issues = self._check_perceivable(page_content, images, page_title)
        results["issues"].extend(perceivable_issues)
        
        # 2. Operable (WCAG Principle 2)
        operable_issues = self._check_operable(forms, page_content)
        results["issues"].extend(operable_issues)
        
        # 3. Understandable (WCAG Principle 3)
        understandable_issues = self._check_understandable(page_content, headings, forms)
        results["issues"].extend(understandable_issues)
        
        # 4. Robust (WCAG Principle 4)
        robust_issues = self._check_robust(page_content)
        results["issues"].extend(robust_issues)
        
        # Calculate compliance score
        results["compliance_score"] = self._calculate_compliance_score(results["issues"])
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results["issues"])
        
        # Identify affected user groups
        results["affected_users"] = self._identify_affected_users(results["issues"])
        
        return results
    
    def _check_perceivable(
        self, 
        page_content: str,
        images: List[Dict[str, Any]],
        page_title: str
    ) -> List[Dict[str, Any]]:
        """Check WCAG Principle 1: Perceivable"""
        issues = []
        
        # 1.1.1 Non-text Content (Level A)
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            issues.append({
                "wcag_sc": "1.1.1",
                "level": "A",
                "principle": "Perceivable",
                "guideline": "Text Alternatives",
                "issue": f"{len(images_without_alt)} images missing alt text",
                "impact": "Screen reader users cannot understand image content",
                "severity": "HIGH",
                "affected_groups": ["Blind users", "Screen reader users"],
                "fix": "Add descriptive alt attributes to all images: <img src='image.jpg' alt='Description'>",
                "code_example": "<img src='logo.png' alt='Company Logo'>"
            })
        
        # 1.3.1 Info and Relationships (Level A)
        if not re.search(r'<h1[^>]*>', page_content, re.IGNORECASE):
            issues.append({
                "wcag_sc": "1.3.1",
                "level": "A",
                "principle": "Perceivable",
                "guideline": "Adaptable",
                "issue": "No H1 heading found",
                "impact": "Page structure unclear to assistive technologies",
                "severity": "MEDIUM",
                "affected_groups": ["Screen reader users", "Cognitive disability users"],
                "fix": "Add a single H1 heading as main page title",
                "code_example": "<h1>Main Page Title</h1>"
            })
        
        # 1.4.1 Use of Color (Level A)
        # Check for color-only indicators
        color_keywords = ['red', 'green', 'blue', 'error', 'success', 'warning']
        color_usage = sum(page_content.lower().count(word) for word in color_keywords)
        if color_usage > 5:
            issues.append({
                "wcag_sc": "1.4.1",
                "level": "A",
                "principle": "Perceivable",
                "guideline": "Distinguishable",
                "issue": "Possible reliance on color alone for information",
                "impact": "Color-blind users may miss important information",
                "severity": "MEDIUM",
                "affected_groups": ["Color-blind users", "Low vision users"],
                "fix": "Use text, icons, or patterns in addition to color",
                "code_example": "<span class='error-icon'>⚠️</span> Error message"
            })
        
        # 1.4.3 Contrast Minimum (Level AA)
        # Note: Actual contrast checking requires rendered page
        issues.append({
            "wcag_sc": "1.4.3",
            "level": "AA",
            "principle": "Perceivable",
            "guideline": "Distinguishable",
            "issue": "Color contrast should be manually verified",
            "impact": "Low contrast text difficult to read",
            "severity": "LOW",
            "affected_groups": ["Low vision users", "Elderly users"],
            "fix": "Ensure contrast ratio of at least 4.5:1 for normal text, 3:1 for large text",
            "code_example": "Use tools like WebAIM Contrast Checker"
        })
        
        # 2.4.2 Page Titled (Level A)
        if not page_title or len(page_title.strip()) < 3:
            issues.append({
                "wcag_sc": "2.4.2",
                "level": "A",
                "principle": "Operable",
                "guideline": "Navigable",
                "issue": "Page title missing or too short",
                "impact": "Users cannot identify page purpose",
                "severity": "HIGH",
                "affected_groups": ["All users", "Screen reader users"],
                "fix": "Add descriptive page title",
                "code_example": "<title>Home - Company Name</title>"
            })
        
        return issues
    
    def _check_operable(self, forms: List[Dict[str, Any]], page_content: str) -> List[Dict[str, Any]]:
        """Check WCAG Principle 2: Operable"""
        issues = []
        
        # 2.1.1 Keyboard (Level A)
        # Check for keyboard trap indicators
        if 'onkeydown' in page_content.lower() or 'onkeypress' in page_content.lower():
            issues.append({
                "wcag_sc": "2.1.1",
                "level": "A",
                "principle": "Operable",
                "guideline": "Keyboard Accessible",
                "issue": "Potential keyboard trap detected",
                "impact": "Keyboard users may get stuck",
                "severity": "HIGH",
                "affected_groups": ["Keyboard-only users", "Motor disability users"],
                "fix": "Ensure all functionality is keyboard accessible and no keyboard traps exist",
                "code_example": "Test with Tab, Shift+Tab, Enter, Escape keys"
            })
        
        # 3.2.2 On Input (Level A)
        # Check forms for proper labels
        for form in forms:
            inputs_without_labels = 0
            for inp in form.get('inputs', []):
                if not inp.get('label') and not inp.get('aria-label'):
                    inputs_without_labels += 1
            
            if inputs_without_labels > 0:
                issues.append({
                    "wcag_sc": "3.2.2",
                    "level": "A",
                    "principle": "Understandable",
                    "guideline": "Predictable",
                    "issue": f"{inputs_without_labels} form inputs without labels",
                    "impact": "Users cannot identify input purpose",
                    "severity": "HIGH",
                    "affected_groups": ["Screen reader users", "Cognitive disability users"],
                    "fix": "Add <label> elements or aria-label attributes to all inputs",
                    "code_example": "<label for='email'>Email:</label><input id='email' type='email'>"
                })
                break
        
        # 2.4.7 Focus Visible (Level AA)
        if ':focus' not in page_content and 'outline' not in page_content:
            issues.append({
                "wcag_sc": "2.4.7",
                "level": "AA",
                "principle": "Operable",
                "guideline": "Navigable",
                "issue": "No visible focus indicators detected",
                "impact": "Keyboard users cannot see which element has focus",
                "severity": "MEDIUM",
                "affected_groups": ["Keyboard-only users", "Motor disability users"],
                "fix": "Ensure focusable elements have visible focus indicators",
                "code_example": "button:focus { outline: 2px solid blue; }"
            })
        
        return issues
    
    def _check_understandable(
        self,
        page_content: str,
        headings: List[str],
        forms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check WCAG Principle 3: Understandable"""
        issues = []
        
        # 3.1.1 Language of Page (Level A)
        if not re.search(r'<html[^>]*\slang=', page_content, re.IGNORECASE):
            issues.append({
                "wcag_sc": "3.1.1",
                "level": "A",
                "principle": "Understandable",
                "guideline": "Readable",
                "issue": "Page language not specified",
                "impact": "Screen readers cannot pronounce text correctly",
                "severity": "MEDIUM",
                "affected_groups": ["Screen reader users", "International users"],
                "fix": "Add lang attribute to <html> tag",
                "code_example": "<html lang='en'>"
            })
        
        # 3.3.1 Error Identification (Level A)
        # Check for error handling in forms
        has_error_handling = any(
            'error' in str(form).lower() or 'invalid' in str(form).lower()
            for form in forms
        )
        if forms and not has_error_handling:
            issues.append({
                "wcag_sc": "3.3.1",
                "level": "A",
                "principle": "Understandable",
                "guideline": "Input Assistance",
                "issue": "Forms lack error identification",
                "impact": "Users cannot identify and correct input errors",
                "severity": "MEDIUM",
                "affected_groups": ["All users", "Cognitive disability users"],
                "fix": "Provide clear error messages for invalid inputs",
                "code_example": "<span role='alert' class='error'>Email is required</span>"
            })
        
        # 3.3.2 Labels or Instructions (Level A)
        for form in forms:
            if not any('required' in str(inp).lower() for inp in form.get('inputs', [])):
                issues.append({
                    "wcag_sc": "3.3.2",
                    "level": "A",
                    "principle": "Understandable",
                    "guideline": "Input Assistance",
                    "issue": "Form fields missing required field indicators",
                    "impact": "Users don't know which fields are mandatory",
                    "severity": "LOW",
                    "affected_groups": ["All users", "Cognitive disability users"],
                    "fix": "Mark required fields clearly",
                    "code_example": "<label>Email <span aria-label='required'>*</span></label>"
                })
                break
        
        return issues
    
    def _check_robust(self, page_content: str) -> List[Dict[str, Any]]:
        """Check WCAG Principle 4: Robust"""
        issues = []
        
        # 4.1.1 Parsing (Level A)
        # Check for common HTML errors
        parsing_errors = []
        
        # Duplicate IDs
        id_pattern = r'id=["\']([^"\']+)["\']'
        ids = re.findall(id_pattern, page_content)
        duplicate_ids = [id for id in ids if ids.count(id) > 1]
        if duplicate_ids:
            parsing_errors.append(f"Duplicate IDs: {set(duplicate_ids)}")
        
        # Unclosed tags (simple check)
        open_tags = len(re.findall(r'<(?!/)(\w+)', page_content))
        close_tags = len(re.findall(r'</(\w+)>', page_content))
        if abs(open_tags - close_tags) > 5:
            parsing_errors.append("Possible unclosed HTML tags")
        
        if parsing_errors:
            issues.append({
                "wcag_sc": "4.1.1",
                "level": "A",
                "principle": "Robust",
                "guideline": "Compatible",
                "issue": f"HTML parsing issues: {', '.join(parsing_errors)}",
                "impact": "Assistive technologies may not parse content correctly",
                "severity": "HIGH",
                "affected_groups": ["Screen reader users", "All assistive technology users"],
                "fix": "Validate HTML and fix parsing errors",
                "code_example": "Use W3C HTML Validator"
            })
        
        # 4.1.2 Name, Role, Value (Level A)
        # Check for ARIA usage
        has_aria = 'aria-' in page_content.lower()
        if not has_aria:
            issues.append({
                "wcag_sc": "4.1.2",
                "level": "A",
                "principle": "Robust",
                "guideline": "Compatible",
                "issue": "No ARIA attributes detected",
                "impact": "Custom UI components may not be accessible",
                "severity": "LOW",
                "affected_groups": ["Screen reader users", "Assistive technology users"],
                "fix": "Add ARIA attributes to custom components",
                "code_example": "<button aria-label='Close dialog' aria-pressed='false'>"
            })
        
        return issues
    
    def _calculate_compliance_score(self, issues: List[Dict[str, Any]]) -> int:
        """Calculate WCAG compliance score (0-100)"""
        if not issues:
            return 100
        
        severity_deductions = {
            'HIGH': 15,
            'MEDIUM': 8,
            'LOW': 3
        }
        
        score = 100
        for issue in issues:
            severity = issue.get('severity', 'LOW')
            score -= severity_deductions.get(severity, 5)
        
        return max(0, score)
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate prioritized recommendations"""
        if not issues:
            return ["✅ No accessibility issues found! Great job!"]
        
        # Group by severity
        high = [i for i in issues if i.get('severity') == 'HIGH']
        medium = [i for i in issues if i.get('severity') == 'MEDIUM']
        low = [i for i in issues if i.get('severity') == 'LOW']
        
        recommendations = []
        
        if high:
            recommendations.append(f"🚨 URGENT: Fix {len(high)} high-severity issues first")
            for issue in high[:3]:  # Top 3
                recommendations.append(f"  • {issue['issue']}: {issue['fix']}")
        
        if medium:
            recommendations.append(f"⚠️ IMPORTANT: Address {len(medium)} medium-severity issues")
            for issue in medium[:2]:  # Top 2
                recommendations.append(f"  • {issue['issue']}: {issue['fix']}")
        
        if low:
            recommendations.append(f"ℹ️ NICE TO HAVE: Consider {len(low)} low-severity improvements")
        
        return recommendations
    
    def _identify_affected_users(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Identify user groups affected by accessibility issues"""
        affected = set()
        for issue in issues:
            affected.update(issue.get('affected_groups', []))
        return sorted(list(affected))
