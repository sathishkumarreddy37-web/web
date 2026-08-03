"""
AI-Powered Test Results Analyzer
Uses available LLM (Google Gemini / OpenAI / Anthropic / Ollama) to provide intelligent insights
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from utils.model_provider import get_llm
from rich.console import Console

console = Console()


class AIAnalyzer:
    """Analyze test results with AI and generate actionable insights"""
    
    def __init__(self, model: str = None):
        """Initialize AI analyzer with specified model (or auto-detect)"""
        self.model = model
        try:
            self.llm = get_llm(model=model)
        except Exception as e:
            console.print(f"[yellow]⚠️  AI initialization warning: {e}[/yellow]")
            self.llm = None
    
    async def analyze_results(self, results: Dict[str, Any]) -> Optional[str]:
        """
        Analyze test results and provide detailed insights
        
        Args:
            results: Dictionary of test results from comprehensive tester
            
        Returns:
            String containing detailed AI-generated insights, or None if unavailable
        """
        if not self.llm:
            return None
        
        try:
            console.print("[cyan]🤖 Analyzing results with AI...[/cyan]")
            prompt = self._build_analysis_prompt(results)
            
            response = await self.llm.ainvoke(prompt)
            insights = response.content
            
            console.print(f"[green]✓ AI analysis complete ({len(insights)} chars)[/green]")
            return insights
            
        except Exception as e:
            console.print(f"[yellow]⚠️  AI analysis unavailable: {e}[/yellow]")
            return None
    
    def analyze_results_sync(self, results: Dict[str, Any]) -> Optional[str]:
        """Synchronous wrapper for analyze_results"""
        try:
            return asyncio.run(self.analyze_results(results))
        except Exception as e:
            console.print(f"[yellow]⚠️  AI analysis failed: {e}[/yellow]")
            return None
    
    def _build_analysis_prompt(self, results: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt for AI"""
        
        tests = results.get('tests', {})
        url = results.get('url', 'Unknown')
        
        # Extract key metrics
        page_load = tests.get('page_load', {})
        load_time = page_load.get('load_time', 0)
        status_code = page_load.get('status_code', 'N/A')
        
        security = tests.get('security', {})
        present_headers = security.get('present_headers', [])
        missing_headers = security.get('missing_headers', [])
        
        accessibility = tests.get('accessibility', {})
        a11y_issues = accessibility.get('issues', 0)
        
        links = tests.get('links', {})
        broken_links = links.get('broken_links', [])
        total_links = links.get('total_links', 0)
        
        forms = tests.get('forms', {})
        form_count = forms.get('form_count', 0)
        
        responsive = tests.get('responsive', {})
        responsive_status = responsive.get('status', 'N/A')
        
        console_errors = tests.get('console_errors', {})
        errors = console_errors.get('errors', 0)
        warnings = console_errors.get('warnings', 0)
        
        prompt = f"""
You are an expert web developer, security analyst, and UX consultant. Analyze these test results for {url}.

═══════════════════════════════════════════════════════════════
TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════════════

🌐 URL: {url}
📅 Tested: {results.get('timestamp', 'N/A')}

⚡ PERFORMANCE:
   • Load Time: {load_time:.2f}s
   • HTTP Status: {status_code}
   • Status: {page_load.get('status', 'N/A')}

🔒 SECURITY:
   • Present Headers: {len(present_headers)} ({', '.join(present_headers[:3]) if present_headers else 'None'})
   • Missing Headers: {len(missing_headers)} ({', '.join(missing_headers[:3]) if missing_headers else 'None'})
   • Status: {security.get('status', 'N/A')}

♿ ACCESSIBILITY:
   • Issues Found: {a11y_issues}
   • Status: {accessibility.get('status', 'N/A')}

🔗 LINKS:
   • Total Links: {total_links}
   • Broken Links: {len(broken_links)}
   • Status: {links.get('status', 'N/A')}

📝 FORMS:
   • Forms Found: {form_count}
   • Status: {forms.get('status', 'N/A')}

📱 RESPONSIVE DESIGN:
   • Status: {responsive_status}

🐛 CONSOLE ERRORS:
   • Errors: {errors}
   • Warnings: {warnings}

═══════════════════════════════════════════════════════════════
DETAILED TEST DATA
═══════════════════════════════════════════════════════════════
{json.dumps(tests, indent=2)}

═══════════════════════════════════════════════════════════════
ANALYSIS REQUIREMENTS
═══════════════════════════════════════════════════════════════

Provide a comprehensive analysis with these sections:

1️⃣ EXECUTIVE SUMMARY (3-4 sentences for stakeholders)
   • Overall site health assessment
   • Key strengths and concerns
   • Quick wins available
   • Business impact

2️⃣ CRITICAL ISSUES (Immediate action required)
   List issues that:
   • Will break functionality
   • Expose security vulnerabilities
   • Create legal/compliance risks
   • Severely impact user experience
   
   Format: 
   🚨 [Issue Name]
      Impact: [What happens if not fixed]
      Priority: [Critical/High/Medium]
      Affected Users: [Percentage or group]

3️⃣ PERFORMANCE ANALYSIS
   • Load time assessment (compare to 3-second standard)
   • User experience impact
   • Mobile vs desktop considerations
   • Specific bottlenecks identified
   • Optimization recommendations with expected improvements
   • Code examples where applicable

4️⃣ SECURITY ASSESSMENT
   • Vulnerability analysis for each missing header
   • Attack vectors and real-world risks
   • Compliance implications (GDPR, OWASP)
   • Fix priority ranking
   • Specific implementation steps
   
   For each missing header, provide:
   • What it protects against
   • Real-world attack example
   • Code to add it
   • Expected security improvement

5️⃣ ACCESSIBILITY CONCERNS
   • WCAG 2.1 compliance level
   • Specific issues breakdown
   • User groups affected (vision, motor, cognitive, hearing)
   • Legal risks (ADA, Section 508)
   • Fix priority and effort
   • Code examples for top 3 issues

6️⃣ USER EXPERIENCE IMPACT
   • How issues affect typical user journey
   • Potential bounce rate impact
   • Conversion funnel implications
   • Mobile experience concerns
   • Trust and credibility factors

7️⃣ RECOMMENDED ACTION PLAN
   
   Quick Wins (< 1 hour):
   • [Action] - Effort: [time] - Impact: [High/Medium/Low] - Priority: P0/P1/P2
   
   High Impact (1-4 hours):
   • [Action] - Effort: [time] - Impact: [High/Medium/Low] - Priority: P0/P1/P2
   
   Long Term (> 4 hours):
   • [Action] - Effort: [time] - Impact: [High/Medium/Low] - Priority: P0/P1/P2

8️⃣ CODE FIX EXAMPLES
   Provide 2-3 complete, copy-paste ready examples:
   
   Example format:
   🔧 Fix: [Issue Name]
   
   BEFORE:
   ```[language]
   [problematic code]
   ```
   
   AFTER:
   ```[language]
   [fixed code]
   ```
   
   WHY: [Explanation of why this fix works]
   IMPACT: [Expected improvement]

9️⃣ ESTIMATED IMPROVEMENTS
   If all fixes are implemented:
   • Performance: [X seconds saved, Y% faster]
   • Security: [Score improves from X to Y]
   • Accessibility: [Compliance level reached]
   • SEO: [Expected ranking impact]
   • User Experience: [Bounce rate change estimate]

🔟 NEXT STEPS
   
   TODAY:
   • [Immediate action 1]
   • [Immediate action 2]
   
   THIS WEEK:
   • [Priority action 1]
   • [Priority action 2]
   • [Priority action 3]
   
   THIS MONTH:
   • [Strategic improvement 1]
   • [Strategic improvement 2]

═══════════════════════════════════════════════════════════════
GUIDELINES
═══════════════════════════════════════════════════════════════

• Use clear, actionable language
• Include specific numbers and metrics
• Provide realistic timelines
• Be honest about severity but constructive
• Focus on business value, not just technical details
• Prioritize by impact × effort ratio
• Give concrete examples over generic advice
• Consider different user contexts (mobile, desktop, accessibility needs)
• Reference industry standards and best practices
• Explain WHY each fix matters, not just WHAT to fix

Begin your analysis now:
"""
        
        return prompt


class AIInsightsCache:
    """Cache AI insights to avoid redundant API calls"""
    
    def __init__(self, cache_file: str = "ai_insights_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        try:
            from pathlib import Path
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            from pathlib import Path
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass
    
    def get_cached_insights(self, url: str, test_hash: str) -> Optional[str]:
        """Get cached insights for a URL and test configuration"""
        cache_key = f"{url}_{test_hash}"
        return self.cache.get(cache_key)
    
    def cache_insights(self, url: str, test_hash: str, insights: str):
        """Cache insights for a URL and test configuration"""
        cache_key = f"{url}_{test_hash}"
        self.cache[cache_key] = {
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()


# Convenience function
async def get_ai_insights(results: Dict[str, Any], use_cache: bool = True) -> Optional[str]:
    """
    Quick function to get AI insights for test results
    
    Args:
        results: Test results dictionary
        use_cache: Whether to use cached insights
        
    Returns:
        AI-generated insights or None
    """
    try:
        analyzer = AIAnalyzer()
        
        if use_cache:
            cache = AIInsightsCache()
            url = results.get('url', 'unknown')
            # Simple hash of test results
            test_hash = str(hash(json.dumps(results.get('tests', {}), sort_keys=True)))
            
            # Check cache
            cached = cache.get_cached_insights(url, test_hash)
            if cached:
                console.print("[cyan]📦 Using cached AI insights[/cyan]")
                return cached.get('insights')
        
        # Generate new insights
        insights = await analyzer.analyze_results(results)
        
        if use_cache and insights:
            cache.cache_insights(url, test_hash, insights)
        
        return insights
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Failed to get AI insights: {e}[/yellow]")
        return None


def get_ai_insights_sync(results: Dict[str, Any], use_cache: bool = True) -> Optional[str]:
    """Synchronous wrapper for get_ai_insights"""
    try:
        return asyncio.run(get_ai_insights(results, use_cache))
    except Exception as e:
        console.print(f"[yellow]⚠️  Failed to get AI insights: {e}[/yellow]")
        return None
