# Claude CLI Configuration for OptiFlight

This directory contains configuration for Claude AI to act as an intelligent assistant for the OptiFlight Coordinator project.

---

## 📚 What's Here

### `instructions.md`
Comprehensive project context for Claude including:
- Project overview and architecture
- Current status (94% complete!)
- Development guidelines
- Common tasks and commands
- Technology stack
- Documentation structure

**Claude reads this automatically** when working in this repository.

---

## 🎯 Available Slash Commands

Use these commands in Claude chat by typing `/command`:

### `/status`
Shows current project status and next steps
- Completion percentage
- What's working vs. what's needed
- Timeline to production

### `/deploy`
Guides you through deploying to an environment
- Staging, pre-prod, or production
- Prerequisites and validation
- Rollback procedures

### `/test`
Helps run comprehensive tests
- Linting and type checking
- Unit and integration tests
- End-to-end workflows
- GitLab pipeline validation

### `/api-integration`
Guides API integration work
- OptiCore, Freya Climb, Freya Level
- OAuth2 implementation
- Code changes needed
- Testing strategy

### `/architecture`
Explains system architecture
- Component overview
- Data flow
- Infrastructure
- Diagrams and references

### `/troubleshoot`
Debug issues systematically
- Common problems and solutions
- Diagnostic commands
- Monitoring tools
- Escalation paths

### `/gitlab`
Help with GitLab CI/CD
- Initial setup (10 steps)
- Understanding pipeline
- CI/CD variables
- Deployment workflows

### `/docs`
Navigate documentation
- Quick links to all docs
- Search by topic
- Documentation index

---

## 🚀 Quick Start

### New Developers
1. Ask Claude: `/status` - Understand where we are
2. Ask Claude: `/docs` - Find relevant documentation
3. Ask Claude: `/architecture` - Learn the system
4. Ask Claude: "How do I run tests locally?"

### Deploying
1. Ask Claude: `/deploy` - Choose your environment
2. Follow step-by-step guide
3. Use provided commands

### Integrating APIs
1. Ask Claude: `/api-integration`
2. Follow the 5-day plan
3. Get code examples and tests

### Debugging
1. Ask Claude: `/troubleshoot`
2. Describe your issue
3. Get systematic diagnosis

---

## 💡 Example Conversations

### "I'm new to this project, what should I know?"
Claude will provide an overview and point to key documentation.

### "How do I deploy to staging?"
Claude will explain the GitLab auto-deployment process.

### "The pipeline is failing on lint errors"
Claude will show you how to run linting locally and fix issues.

### "What's the timeline to production?"
Claude will reference the 2-week plan and current blockers.

### "How do I connect the real OptiCore API?"
Claude will guide you through API integration with code examples.

---

## 📖 Documentation Structure

All documentation is organized in `docs/`:

```
docs/
├── production/           # Production deployment guides
│   ├── PRODUCTION-DEPLOYMENT-SUMMARY.md
│   ├── PRODUCTION-READINESS-CHECKLIST.md
│   ├── PRODUCTION-SECRETS-TEMPLATE.md
│   └── QUICK-START-PRODUCTION.md
├── gitlab/              # GitLab CI/CD setup
│   ├── GITLAB-PRODUCTION-READY.md
│   ├── GITLAB-CI-CD-GUIDE.md
│   └── GITLAB-SETUP-CHECKLIST.md
├── api-integration/     # API integration guides
│   └── REAL-API-INTEGRATION-GUIDE.md
└── guides/              # Architecture & general guides
    ├── ARCHITECTURE-FLOW-GUIDE.md
    ├── DEPLOYMENT-GUIDE.md
    └── INTEGRATION-TEST-REPORT.md
```

---

## 🔍 How It Works

1. **instructions.md** is automatically loaded when Claude starts
2. Claude has context about the project, architecture, and status
3. Slash commands in `commands/` provide specialized help
4. Claude references docs in real-time for accurate answers

---

## ✅ Benefits

### For Developers
- **Instant answers** without searching docs
- **Step-by-step guidance** for complex tasks
- **Code examples** for common operations
- **Up-to-date context** about project status

### For DevOps
- **Deployment guidance** with exact commands
- **Troubleshooting help** with diagnostic steps
- **GitLab setup** instructions
- **Monitoring** and rollback procedures

### For New Team Members
- **Quick onboarding** with project overview
- **Architecture understanding** with explanations
- **Documentation navigation** without getting lost
- **Best practices** automatically suggested

---

## 🎯 Best Practices

### When Asking Claude
- Be specific about what you're trying to do
- Mention the environment (local, staging, prod)
- Include error messages if debugging
- Use slash commands for common tasks

### When Claude Suggests Code
- Review before running
- Check that it fits the codebase style
- Run tests after changes
- Commit with conventional commit messages

### When Following Guides
- Claude will reference exact documentation
- Follow the linked docs for comprehensive info
- Claude provides quick summaries, docs have details

---

## 🔄 Keeping Updated

### When Project Changes
Update relevant files:
- `instructions.md` - For major changes (new phases, architecture)
- `commands/*.md` - For new common workflows
- Documentation in `docs/` - For detailed procedures

### When Adding Features
- Update architecture references
- Add new commands if needed
- Keep status up to date

---

## 📞 Support

### Claude Can Help With
- Understanding code and architecture
- Deployment procedures
- Troubleshooting issues
- Finding documentation
- Writing tests
- Code reviews

### Claude Cannot
- Access external services (OptiCore, Freya)
- Run commands (you'll need to run them)
- Make decisions requiring business context
- Access production systems directly

---

## 🎉 Get Started Now!

Try it out:
```
Ask Claude: /status
```

Or just ask naturally:
```
"How do I set up GitLab CI/CD?"
"What's the fastest way to run tests?"
"Help me debug a failing pod"
```

Claude is ready to help! 🚀

---

**Last Updated:** 2025-11-25
**Claude CLI Version:** Latest
**Project:** OptiFlight Coordinator
