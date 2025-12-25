"""
Maker-Checker Validation Agent

This agent validates analysis results before publishing.
Prevents errors like misclassifying GitHub repos as tools.
"""
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import httpx
from urllib.parse import urlparse
import structlog

logger = structlog.get_logger()


@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    confidence: float  # 0-100
    issues: List[str]
    recommendations: List[str]
    corrected_data: Optional[Dict[str, Any]] = None


class ToolValidator:
    """
    Validates AI tool analysis results.
    Acts as a 'checker' in the maker-checker pattern.
    """
    
    # Domains that are NOT AI tools themselves
    NON_TOOL_DOMAINS = [
        # Code hosting
        "github.com", "gitlab.com", "bitbucket.org", "codeberg.org",
        # Package registries  
        "pypi.org", "npmjs.com", "rubygems.org", "crates.io",
        # Documentation
        "docs.google.com", "notion.so", "confluence.atlassian.com",
        # Social/Community
        "twitter.com", "x.com", "linkedin.com", "discord.com", "slack.com",
        "reddit.com", "news.ycombinator.com", "medium.com", "substack.com",
        # General platforms
        "youtube.com", "vimeo.com", "soundcloud.com", "spotify.com",
        "wikipedia.org", "wikimedia.org",
    ]
    
    # Domains that should be the product itself
    KNOWN_AI_TOOL_DOMAINS = {
        "openai.com": "OpenAI",
        "anthropic.com": "Anthropic", 
        "google.com/ai": "Google AI",
        "midjourney.com": "Midjourney",
        "cursor.com": "Cursor",
        "copilot.github.com": "GitHub Copilot",
        "jasper.ai": "Jasper",
        "writesonic.com": "Writesonic",
        "perplexity.ai": "Perplexity",
    }
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
    
    async def validate_tool(self, tool_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate tool data before publishing.
        
        Checks:
        1. URL is an actual AI tool (not a code repo, doc site, etc.)
        2. Name matches the actual product/company
        3. Analysis makes sense for the tool type
        """
        issues = []
        recommendations = []
        corrected = tool_data.copy()
        
        url = tool_data.get("url", "")
        name = tool_data.get("name", "")
        
        # Check 1: URL validation
        url_valid, url_issues = self._validate_url(url)
        if not url_valid:
            issues.extend(url_issues)
        
        # Check 2: Name extraction validation
        name_valid, name_issues, suggested_name = await self._validate_name(url, name)
        if not name_valid:
            issues.extend(name_issues)
            if suggested_name:
                recommendations.append(f"Consider renaming to: {suggested_name}")
                corrected["name"] = suggested_name
        
        # Check 3: Wrapper analysis sanity check
        wrapper_valid, wrapper_issues = self._validate_wrapper_analysis(tool_data)
        if not wrapper_valid:
            issues.extend(wrapper_issues)
        
        # Check 4: Trust score sanity
        trust_valid, trust_issues = self._validate_trust_score(tool_data)
        if not trust_valid:
            issues.extend(trust_issues)
        
        # Calculate overall validity
        is_valid = len([i for i in issues if "CRITICAL" in i]) == 0
        confidence = max(0, 100 - (len(issues) * 15))
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            corrected_data=corrected if corrected != tool_data else None,
        )
    
    def _validate_url(self, url: str) -> Tuple[bool, List[str]]:
        """Check if URL is a valid AI tool URL"""
        issues = []
        
        if not url:
            return False, ["CRITICAL: No URL provided"]
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Check for non-tool domains
            for non_tool in self.NON_TOOL_DOMAINS:
                if non_tool in domain:
                    # Special case: GitHub repo pages
                    if "github.com" in domain:
                        issues.append(f"CRITICAL: GitHub repository URL detected - this is a code repo, not a tool website")
                        issues.append("INFO: GitHub URLs should only be used for the tool's source code, not as the main tool URL")
                    else:
                        issues.append(f"WARNING: URL domain '{domain}' is typically not an AI tool website")
            
            # Check for suspicious paths
            if "/blob/" in path or "/tree/" in path or "/commit/" in path:
                issues.append("CRITICAL: URL appears to be a code repository file/folder link")
            
            if "/wiki/" in path:
                issues.append("WARNING: URL appears to be a wiki page, not a product page")
                
        except Exception as e:
            issues.append(f"ERROR: Invalid URL format - {str(e)}")
            return False, issues
        
        return len([i for i in issues if "CRITICAL" in i]) == 0, issues
    
    async def _validate_name(self, url: str, name: str) -> Tuple[bool, List[str], Optional[str]]:
        """Validate and potentially correct the tool name"""
        issues = []
        suggested_name = None
        
        if not name:
            issues.append("CRITICAL: No name provided")
            return False, issues, None
        
        # Check for generic platform names being used as tool names
        generic_names = ["github", "gitlab", "npm", "pypi", "docs", "api", "app"]
        if name.lower() in generic_names:
            issues.append(f"CRITICAL: '{name}' is a generic platform name, not a specific tool name")
            
            # Try to extract real name from URL
            try:
                parsed = urlparse(url)
                
                # For GitHub repos, extract the repo name
                if "github.com" in parsed.netloc:
                    parts = parsed.path.strip("/").split("/")
                    if len(parts) >= 2:
                        suggested_name = parts[1]  # repo name
                        issues.append(f"INFO: Detected GitHub repo '{parts[0]}/{parts[1]}'")
                        issues.append(f"CRITICAL: Should not process GitHub repos as tools")
                else:
                    # Use domain name as potential tool name
                    domain = parsed.netloc.replace("www.", "")
                    suggested_name = domain.split(".")[0].title()
                    
            except Exception:
                pass
        
        # Check for known tool domains
        try:
            parsed = urlparse(url)
            for domain, known_name in self.KNOWN_AI_TOOL_DOMAINS.items():
                if domain in url:
                    if name.lower() != known_name.lower():
                        issues.append(f"INFO: Name mismatch - detected '{domain}' but named '{name}'")
                        suggested_name = known_name
        except Exception:
            pass
        
        return len([i for i in issues if "CRITICAL" in i]) == 0, issues, suggested_name
    
    def _validate_wrapper_analysis(self, tool_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate wrapper/trust analysis makes sense"""
        issues = []
        
        wrapper_status = tool_data.get("wrapper_status", "")
        wrapper_likelihood = tool_data.get("wrapper_likelihood", 0)
        api_dependencies = tool_data.get("api_dependencies", [])
        
        # Check for contradictions
        if wrapper_status == "native" and wrapper_likelihood > 70:
            issues.append("WARNING: Classified as 'native' but high wrapper likelihood detected")
        
        if wrapper_status == "wrapper" and wrapper_likelihood < 30:
            issues.append("WARNING: Classified as 'wrapper' but low wrapper likelihood detected")
        
        # Check for known API providers being marked as wrappers
        url = tool_data.get("url", "")
        known_native_domains = ["openai.com", "anthropic.com", "google.com", "microsoft.com", "meta.com", "mistral.ai"]
        for domain in known_native_domains:
            if domain in url and wrapper_status == "wrapper":
                issues.append(f"CRITICAL: {domain} is an AI provider, not a wrapper!")
        
        return len([i for i in issues if "CRITICAL" in i]) == 0, issues
    
    def _validate_trust_score(self, tool_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate trust score is reasonable"""
        issues = []
        
        trust_score = tool_data.get("trust_score", 0)
        
        if trust_score < 0 or trust_score > 100:
            issues.append(f"CRITICAL: Invalid trust score: {trust_score} (must be 0-100)")
        
        # Check for suspiciously perfect scores
        if trust_score == 100:
            issues.append("WARNING: Perfect 100 trust score is suspicious - manual review recommended")
        
        if trust_score == 0:
            issues.append("WARNING: Zero trust score indicates analysis failure")
        
        return len([i for i in issues if "CRITICAL" in i]) == 0, issues
    
    async def close(self):
        await self.client.aclose()


class ContentValidator:
    """
    Validates content before publishing.
    Ensures quality and accuracy.
    """
    
    def __init__(self):
        self.tool_validator = ToolValidator()
    
    async def validate_before_publish(
        self, 
        content_type: str, 
        data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Main validation entry point.
        Returns validation result with issues and recommendations.
        """
        if content_type == "tool":
            return await self.tool_validator.validate_tool(data)
        else:
            # For other content types, basic validation
            issues = []
            if not data.get("title") and not data.get("name"):
                issues.append("CRITICAL: Content has no title/name")
            if not data.get("url") and not data.get("source_url"):
                issues.append("WARNING: Content has no source URL")
            
            return ValidationResult(
                is_valid=len([i for i in issues if "CRITICAL" in i]) == 0,
                confidence=max(0, 100 - (len(issues) * 20)),
                issues=issues,
                recommendations=[],
            )
    
    async def close(self):
        await self.tool_validator.close()


# Quick test function
async def test_validator():
    """Test the validator with sample data"""
    validator = ContentValidator()
    
    # Test 1: Valid tool
    valid_tool = {
        "name": "Cursor",
        "url": "https://cursor.com",
        "trust_score": 85,
        "wrapper_status": "native",
        "wrapper_likelihood": 15,
    }
    result = await validator.validate_before_publish("tool", valid_tool)
    print(f"\n✅ Valid tool test:")
    print(f"   Valid: {result.is_valid}, Confidence: {result.confidence}")
    print(f"   Issues: {result.issues}")
    
    # Test 2: GitHub repo (should fail)
    github_repo = {
        "name": "GitHub",
        "url": "https://github.com/anthropics/anthropic-cookbook",
        "trust_score": 45,
        "wrapper_status": "wrapper",
        "wrapper_likelihood": 65,
    }
    result = await validator.validate_before_publish("tool", github_repo)
    print(f"\n❌ GitHub repo test (should fail):")
    print(f"   Valid: {result.is_valid}, Confidence: {result.confidence}")
    print(f"   Issues: {result.issues}")
    print(f"   Recommendations: {result.recommendations}")
    
    # Test 3: Misnamed tool
    misnamed = {
        "name": "API",
        "url": "https://www.jasper.ai",
        "trust_score": 75,
        "wrapper_status": "native",
    }
    result = await validator.validate_before_publish("tool", misnamed)
    print(f"\n⚠️ Misnamed tool test:")
    print(f"   Valid: {result.is_valid}, Confidence: {result.confidence}")
    print(f"   Issues: {result.issues}")
    print(f"   Corrected name: {result.corrected_data.get('name') if result.corrected_data else 'N/A'}")
    
    await validator.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_validator())

