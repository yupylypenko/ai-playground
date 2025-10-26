# Pull Request Description Template

## 📝 Template for PR Creation

When creating a pull request, use this template to ensure comprehensive and meaningful descriptions.

```markdown
## Summary
<!-- Brief one-sentence summary of what this PR does -->

## Changes
<!-- List of key changes in this PR -->
- [ ] Change 1
- [ ] Change 2
- [ ] Change 3

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Breaking change

## Description
<!-- Detailed description of the changes, motivation, and context -->

### What Changed?
<!-- What files/components were modified? -->

### Why These Changes?
<!-- What problem does this solve? What is the motivation? -->

### How to Test?
<!-- Steps to test or verify the changes -->

## Screenshots/Demo
<!-- Include screenshots if applicable -->

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented (if needed)
- [ ] Documentation updated (if needed)
- [ ] Tests added/updated (if needed)
- [ ] No breaking changes (or documented if breaking)

## Related Issues
<!-- Link to related issues: Closes #123, Related to #456 -->

## Additional Notes
<!-- Any additional information, concerns, or notes for reviewers -->
```

## Example Usage

### For Documentation PR

```markdown
## Summary
Add comprehensive architecture documentation with PlantUML diagrams and project scaffold

## Changes
- [x] Created complete documentation structure in docs/ folder
- [x] Generated 6 PlantUML diagrams for architecture visualization
- [x] Added embedded PNG diagram images
- [x] Created project scaffold with modular structure
- [x] Added requirements.txt and configuration files

## Type of Change
- [x] Documentation update

## Description

This PR adds comprehensive documentation for the Cosmic Flight Simulator project including:

### What Changed?
- **New Documentation**: Added 6 documentation files in `docs/` folder
  - `ARCHITECTURE.md` - System architecture with embedded diagrams
  - `DIAGRAMS.md` - PlantUML source code for all diagrams
  - `IMPLEMENTATION.md` - Development roadmap
  - `REQUIREMENTS.md` - Feature specifications
  - `SETUP.md` - Installation guide
  - `README.md` - Documentation index

- **Diagram Images**: Generated 6 PNG images from PlantUML
  - System Architecture Diagram
  - Class Diagram
  - Data Flow Sequence
  - Component Interaction
  - Deployment Architecture
  - Mission State Flow

- **Project Scaffold**: Created complete directory structure
  - `src/` - Modular source code (simulator, cockpit, visualization)
  - `tests/` - Test structure
  - `assets/` - Game assets directories
  - `missions/` - Mission files

### Why These Changes?
- Provides clear visual documentation of system architecture
- Enables better understanding for new developers
- Creates foundation for implementation
- Includes all project requirements and setup instructions

### How to Test?
1. View the documentation files in `docs/` folder
2. Check diagrams are embedded correctly
3. Verify PlantUML diagrams can be viewed online
4. Review project structure is complete

## Screenshots/Demo
- Architecture diagrams are embedded in `docs/ARCHITECTURE.md`
- PlantUML source code available in `docs/DIAGRAMS.md`

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Documentation updated
- [x] No breaking changes

## Related Issues
Related to: #IssueNumber (if any)

## Additional Notes
This is a documentation-only PR that establishes the foundation for the Cosmic Flight Simulator project.
```

## Quick Reference

### Essential Sections
1. **Summary** - One sentence overview
2. **Changes** - Key modifications
3. **Description** - Detailed explanation
4. **Type of Change** - Category selection

### Best Practices
- Use clear, descriptive commit messages
- Include "Why" along with "What"
- Add screenshots for visual changes
- Link related issues
- Request specific feedback if needed

## Automation Tips

For GitHub CLI:
```bash
# Create PR with inline description
gh pr create --title "Title" --body "Description"

# Create PR from file
gh pr create --title "Title" --body-file description.md

# Create PR with labels
gh pr create --title "Title" --body "Description" --label "documentation"
```
