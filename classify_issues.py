"""Fetch and classify GitHub issues by risk level."""
import json
import sys
import urllib.request
from typing import List, Dict, Any

repo = "yupylypenko/ai-playground"
url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100"


def classify_risk(issue: Dict[str, Any]) -> str:
    """Classify issue risk level based on title, labels, and content."""
    title_lower = issue.get("title", "").lower()
    body_lower = issue.get("body", "").lower()
    labels = [label["name"].lower() for label in issue.get("labels", [])]
    
    # High risk indicators
    high_risk_keywords = [
        "security", "vulnerability", "exploit", "crash", "data loss",
        "corruption", "critical", "urgent", "breaking", "regression",
        "production", "outage", "down", "broken", "fatal", "error",
        "exception", "memory leak", "race condition", "deadlock"
    ]
    
    # Medium risk indicators
    medium_risk_keywords = [
        "bug", "fix", "issue", "problem", "incorrect", "wrong",
        "performance", "slow", "optimization", "refactor", "technical debt",
        "improvement", "enhancement", "feature", "missing", "incomplete"
    ]
    
    # Check labels first
    if any(keyword in " ".join(labels) for keyword in high_risk_keywords):
        return "High"
    if "security" in labels or "critical" in labels or "bug" in labels:
        return "High"
    
    # Check title and body
    title_body = f"{title_lower} {body_lower}"
    
    if any(keyword in title_body for keyword in high_risk_keywords):
        return "High"
    if any(keyword in title_body for keyword in medium_risk_keywords):
        return "Medium"
    
    # Default to Low for documentation, questions, etc.
    if any(keyword in labels for keyword in ["documentation", "question", "discussion"]):
        return "Low"
    
    return "Low"


def main():
    """Fetch issues and classify them."""
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            issues = [i for i in data if "pull_request" not in i]  # Filter out PRs
            
            if not issues:
                print("## GitHub Issues Risk Classification\n")
                print("**Status**: No open issues found in the repository.\n")
                print("The repository currently has 0 open issues that need triage.")
                return
            
            # Classify each issue
            classified = []
            for issue in issues:
                risk = classify_risk(issue)
                labels = [label["name"] for label in issue.get("labels", [])]
                classified.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "labels": labels,
                    "risk": risk,
                    "url": issue["html_url"]
                })
            
            # Sort by risk (High, Medium, Low)
            risk_order = {"High": 0, "Medium": 1, "Low": 2}
            classified.sort(key=lambda x: (risk_order[x["risk"]], x["number"]))
            
            # Generate markdown output
            print("## GitHub Issues Risk Classification\n")
            print(f"**Total Open Issues**: {len(classified)}\n")
            print("---\n")
            
            current_risk = None
            for issue in classified:
                if issue["risk"] != current_risk:
                    if current_risk is not None:
                        print()
                    print(f"### {issue['risk']} Risk\n")
                    current_risk = issue["risk"]
                
                labels_str = ", ".join(issue["labels"]) if issue["labels"] else "_No labels_"
                print(f"**#{issue['number']}**: [{issue['title']}]({issue['url']})")
                print(f"- **Labels**: {labels_str}")
                print(f"- **Risk Level**: {issue['risk']}")
                print()
            
    except Exception as e:
        print(f"Error fetching issues: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

