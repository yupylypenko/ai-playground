# GitHub Issues Risk Classification

**Generated**: 2025-12-11  
**Repository**: [yupylypenko/ai-playground](https://github.com/yupylypenko/ai-playground)

## Current Status

**Total Open Issues**: 0

The repository currently has no open issues that require triage.

---

## Classification Methodology

Issues are classified into three risk levels based on:

### High Risk
- **Keywords**: security, vulnerability, exploit, crash, data loss, corruption, critical, urgent, breaking, regression, production, outage, down, broken, fatal, error, exception, memory leak, race condition, deadlock
- **Labels**: `security`, `critical`, `bug` (in combination with severity indicators)
- **Impact**: Issues that could cause system failures, data loss, security breaches, or production outages

### Medium Risk
- **Keywords**: bug, fix, issue, problem, incorrect, wrong, performance, slow, optimization, refactor, technical debt, improvement, enhancement, feature, missing, incomplete
- **Impact**: Issues that affect functionality or performance but don't pose immediate critical threats

### Low Risk
- **Keywords**: documentation, question, discussion, enhancement (non-critical), feature request
- **Impact**: Non-critical improvements, documentation updates, questions, or minor enhancements

---

## Example Output Format

When issues exist, the output will be formatted as follows:

```markdown
## GitHub Issues Risk Classification

**Total Open Issues**: 5

---

### High Risk

**#42**: [Critical security vulnerability in authentication](https://github.com/yupylypenko/ai-playground/issues/42)
- **Labels**: security, critical, bug
- **Risk Level**: High

---

### Medium Risk

**#38**: [Performance issue with physics calculations](https://github.com/yupylypenko/ai-playground/issues/38)
- **Labels**: performance, bug
- **Risk Level**: Medium

**#41**: [Missing error handling in API endpoints](https://github.com/yupylypenko/ai-playground/issues/41)
- **Labels**: bug, api
- **Risk Level**: Medium

---

### Low Risk

**#39**: [Update README with new installation steps](https://github.com/yupylypenko/ai-playground/issues/39)
- **Labels**: documentation
- **Risk Level**: Low

**#40**: [Feature request: Add new spacecraft type](https://github.com/yupylypenko/ai-playground/issues/40)
- **Labels**: enhancement, feature
- **Risk Level**: Low
```

---

## Usage

To generate this report, run:

```bash
python classify_issues.py
```

The script will:
1. Fetch all open issues from the repository
2. Classify each issue by risk level
3. Generate a markdown report sorted by risk (High → Medium → Low)

---

## Notes

- Pull requests are automatically excluded from this classification
- Issues are sorted by risk level, then by issue number
- The classification is based on automated keyword and label analysis
- Manual review may be needed for edge cases


