"""
Visual Regression Testing Module
Compares screenshots across test runs to detect UI changes automatically
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class VisualRegressionTester:
    """Detect visual changes between test runs"""
    
    def __init__(self, baseline_dir: str = "visual_baselines", threshold: float = 0.05):
        """
        Initialize visual regression tester
        
        Args:
            baseline_dir: Directory to store baseline images
            threshold: Acceptable difference threshold (0.0-1.0)
        """
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.threshold = threshold
        self.results = []
        
    def capture_baseline(self, page_name: str, screenshot_data: bytes) -> Dict[str, Any]:
        """
        Capture baseline image for comparison
        
        Args:
            page_name: Name/identifier for the page
            screenshot_data: Screenshot bytes data
            
        Returns:
            Baseline info dictionary
        """
        try:
            # Generate baseline filename
            baseline_name = f"baseline_{page_name}.png"
            baseline_path = self.baseline_dir / baseline_name
            
            # Save screenshot data as baseline
            with open(baseline_path, 'wb') as f:
                f.write(screenshot_data)
            
            return {
                "status": "baseline_created",
                "baseline_path": str(baseline_path),
                "page_name": page_name,
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def compare_with_baseline(
        self, 
        page_name: str,
        current_screenshot_data: bytes
    ) -> Dict[str, Any]:
        """
        Compare current screenshot with baseline
        
        Args:
            page_name: Name/identifier for the page
            current_screenshot_data: Screenshot bytes data
            
        Returns:
            Comparison results dictionary
        """
        try:
            # Find baseline
            baseline_name = f"baseline_{page_name}.png"
            baseline_path = self.baseline_dir / baseline_name
            
            if not baseline_path.exists():
                return {
                    "status": "no_baseline",
                    "message": "No baseline found. Run capture_baseline() first.",
                    "page_name": page_name,
                    "passed": False,
                    "difference_percentage": 100.0
                }
            
            # For now, simple comparison (in real scenario would use PIL)
            # Read baseline data
            with open(baseline_path, 'rb') as f:
                baseline_data = f.read()
            
            # Simple byte comparison
            if baseline_data == current_screenshot_data:
                diff_percent = 0.0
            else:
                # Simplified: calculate percentage of different bytes
                min_len = min(len(baseline_data), len(current_screenshot_data))
                if min_len > 0:
                    different_bytes = sum(1 for i in range(min_len) if baseline_data[i] != current_screenshot_data[i])
                    diff_percent = (different_bytes / min_len) * 100
                else:
                    diff_percent = 100.0
            
            # Determine if change is significant
            is_significant = diff_percent > (self.threshold * 100)
            
            result = {
                "status": "compared",
                "page_name": page_name,
                "baseline_path": str(baseline_path),
                "difference_percentage": round(diff_percent, 2),
                "threshold_percentage": round(self.threshold * 100, 2),
                "is_significant_change": is_significant,
                "passed": not is_significant,
                "verdict": "FAIL" if is_significant else "PASS",
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            return {"status": "error", "reason": str(e), "page_name": page_name, "passed": False}
        """Calculate percentage of different pixels"""
        # Convert to grayscale and get histogram
        gray_diff = diff_img.convert('L')
        histogram = gray_diff.histogram()
        
        # Count non-zero pixels (different pixels)
        different_pixels = sum(histogram[1:])
        total_pixels = size[0] * size[1]
        
        return different_pixels / total_pixels if total_pixels > 0 else 0.0
    
    def _generate_diff_image(
        self, 
        baseline: Image.Image, 
        current: Image.Image, 
        diff: Image.Image, 
        url: str
    ) -> str:
        """Generate side-by-side comparison image with diff highlights"""
        try:
            # Create combined image (baseline | current | diff)
            width, height = baseline.size
            combined = Image.new('RGB', (width * 3 + 40, height + 80), 'white')
            
            # Paste images
            combined.paste(baseline, (10, 50))
            combined.paste(current, (width + 20, 50))
            
            # Highlight differences in red
            diff_highlighted = current.copy()
            diff_mask = diff.convert('L')
            diff_highlighted.paste((255, 0, 0), (0, 0), diff_mask)
            combined.paste(diff_highlighted, (width * 2 + 30, 50))
            
            # Add labels
            draw = ImageDraw.Draw(combined)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((width // 2 - 30, 20), "BASELINE", fill='black', font=font)
            draw.text((width + width // 2 - 20, 20), "CURRENT", fill='black', font=font)
            draw.text((width * 2 + width // 2 - 40, 20), "DIFFERENCES", fill='red', font=font)
            
            # Save
            safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            diff_filename = f"diff_{safe_url}_{timestamp}.png"
            diff_path = self.baseline_dir / diff_filename
            combined.save(diff_path)
            
            return str(diff_path)
            
        except Exception as e:
            return f"Error generating diff image: {e}"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all comparisons"""
        if not self.results:
            return {"status": "no_comparisons", "total": 0}
        
        passed = sum(1 for r in self.results if r.get("passed"))
        failed = sum(1 for r in self.results if not r.get("passed"))
        
        significant_changes = [
            {
                "page_name": r["page_name"],
                "diff_percentage": r["difference_percentage"],
                "passed": r["passed"]
            }
            for r in self.results 
            if r.get("is_significant_change")
        ]
        
        return {
            "status": "complete",
            "total_comparisons": len(self.results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / len(self.results) * 100, 1) if self.results else 0,
            "threshold_used": round(self.threshold * 100, 2),
            "significant_changes": significant_changes
        }
    
    def export_report(self, output_path: str = "visual_regression_report.json") -> str:
        """Export detailed comparison report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "details": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path
