# Branching Strategy

## Overview

This repository uses a Git Flow branching strategy optimized for CI/CD with multiple environments.

## Branch Structure

```
main (production)
  ↑
staging (pre-production)
  ↑
dev (development)
  ↑
feature/* (features)
hotfix/* (urgent fixes)
```

## Branches

### `dev` - Development branch

- **Purpose**: Active development and integration
- **Deployment**: Automatically deploys to DEV environment
- **Protection**: Required PR reviews, passing CI
- **Workflow**:
  1. Create feature branch from `dev`
  2. Develop and test locally
  3. Create PR to `dev`
  4. After approval and CI pass, merge
  5. Automatic deployment to DEV

### `staging` - Staging branch

- **Purpose**: Pre-production testing and validation
- **Deployment**: Automatically deploys to STAGING environment
- **Protection**: Required PR reviews, passing CI, additional checks
- **Workflow**:
  1. Create PR from `dev` to `staging`
  2. QA testing in staging environment
  3. After validation, merge
  4. Automatic deployment to STAGING

### `main` - Production branch

- **Purpose**: Production-ready code
- **Deployment**: Deploys to PRODUCTION with approval
- **Protection**: Required PR reviews, admin approval, passing CI
- **Workflow**:
  1. Create PR from `staging` to `main`
  2. Full review and approval process
  3. Merge after approvals
  4. Manual approval required for production deployment

## Feature Development Workflow

```bash
# 1. Start from dev branch
git checkout dev
git pull origin dev

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "feat: description of changes"

# 4. Push feature branch
git push origin feature/your-feature-name

# 5. Create Pull Request to dev
# (Use GitHub UI or gh CLI)

# 6. After review and approval, merge PR
# 7. Delete feature branch
git branch -d feature/your-feature-name
```

## Hotfix Workflow

For urgent production fixes:

```bash
# 1. Create hotfix from main
git checkout main
git checkout -b hotfix/critical-fix

# 2. Make fix and test
git add .
git commit -m "hotfix: description"

# 3. Push and create PR to main
git push origin hotfix/critical-fix

# 4. After approval, merge to main
# 5. Cherry-pick to staging and dev
git checkout staging
git cherry-pick <commit-hash>
git push origin staging

git checkout dev
git cherry-pick <commit-hash>
git push origin dev
```

## Release Process

### Dev → Staging

1. Ensure all features are tested in DEV
2. Create PR from `dev` to `staging`
3. QA team tests in STAGING environment
4. Fix any issues in `dev` and merge to `staging`
5. Once stable, proceed to production

### Staging → Production

1. Create PR from `staging` to `main`
2. Final review by tech leads
3. Deployment checklist completed
4. Merge PR
5. Approve production deployment in GitHub Actions
6. Monitor deployment
7. Rollback if issues detected

## Environment Mappings

| Branch | Environment | Auto-Deploy | Approval Required |
|--------|-------------|-------------|-------------------|
| `dev` | Development | ✅ Yes | ❌ No |
| `staging` | Staging | ✅ Yes | ❌ No |
| `main` | Production | ⚠️ Manual | ✅ Yes |

## Branch Protection Rules

### `dev` Branch
- Require pull request before merging
- Require 1 approval
- Require status checks to pass (CI)
- No force pushes
- No deletions

### `staging` Branch
- Require pull request before merging
- Require 2 approvals
- Require status checks to pass (CI + additional checks)
- No force pushes
- No deletions

### `main` Branch
- Require pull request before merging
- Require 2 approvals (including code owner)
- Require status checks to pass (all checks)
- Require conversation resolution
- No force pushes
- No deletions
- Require signed commits (recommended)

## Commit Message Convention

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(api): add user authentication endpoint
fix(ui): resolve navigation menu bug
docs(readme): update installation instructions
```

## CI/CD Integration

- **Push to `dev`**: Runs CI → Deploys to DEV
- **Push to `staging`**: Runs CI → Deploys to STAGING
- **Push to `main`**: Runs CI → Waits for approval → Deploys to PRODUCTION

## Monitoring and Rollback

After deployment:
1. Check application health
2. Monitor logs and metrics
3. If issues detected:
   ```bash
   # Quick rollback
   git revert <commit-hash>
   git push origin <branch>
   ```

## Best Practices

1. **Keep branches up to date**: Regularly sync with upstream
2. **Small, focused PRs**: Easier to review and merge
3. **Write tests**: All features should have tests
4. **Document changes**: Update docs with code changes
5. **Review thoroughly**: Code review is critical
6. **Test in lower environments**: Verify in DEV/STAGING before PROD

## Troubleshooting

### Merge Conflicts

```bash
# Update your branch with latest from target
git checkout your-branch
git fetch origin
git merge origin/dev  # or staging/main

# Resolve conflicts
# git status shows conflicted files
# Edit files to resolve
git add resolved-files
git commit
```

### Failed Deployments

1. Check GitHub Actions logs
2. Verify environment variables/secrets
3. Check application logs in cloud provider
4. Roll back if necessary
5. Fix issue in feature branch
6. Re-deploy

---

**Questions?** Contact DevOps team or check [CI/CD documentation](.github/workflows/README.md)
