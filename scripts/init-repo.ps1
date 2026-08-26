# ==========================================================
# Startup Canvas — One-shot git init + first push helper
# ==========================================================
# Usage (PowerShell 5.1+):
#   .\scripts\init-repo.ps1 -RemoteUrl 'git@github.com:<owner>/startup-canvas.git'
# or
#   .\scripts\init-repo.ps1 -RemoteUrl 'https://github.com/<owner>/startup-canvas.git'
#
# What it does:
#   1. Initialises a git repo (only if not already initialised)
#   2. Sets the branch to `main`
#   3. Configures sane defaults (autocrlf=false, pull=rebase)
#   4. Adds a `.gitattributes` for line ending consistency
#   5. Stages everything, commits with a Conventional Commit message
#   6. Renames the branch to `main` if necessary
#   7. Adds the remote `origin`, then `git push -u origin main`
#
# Requires: Git for Windows >= 2.30 in PATH.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteUrl,

    [string]$DefaultBranch = 'main',
    [string]$InitialMessage = 'chore: initial commit (green CI)',
    [string]$UserName = 'Startup Canvas',
    [string]$UserEmail = 'bot@startup-canvas.example'
)

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSCommandPath) | Out-Null
Set-Location (Resolve-Path '..') | Out-Null

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

Step "1/8 - Initialising git repository (if needed)"
if (-not (Test-Path '.git')) {
    git init --initial-branch=$DefaultBranch | Out-Null
    Write-Host "  created .git"
} else {
    Write-Host "  already a git repo"
}

Step "2/8 - Setting git defaults"
git config core.autocrlf false
git config pull.rebase true
git config init.defaultBranch $DefaultBranch

Step "3/8 - Configuring local committer"
git config user.name  $UserName
git config user.email $UserEmail

Step "4/8 - Writing .gitattributes"
@'
# Auto-detect text files
* text=auto

# Source files: force LF to keep docker / shell scripts portable
*.py            text eol=lf
*.js            text eol=lf
*.ts            text eol=lf
*.tsx           text eol=lf
*.json          text eol=lf
*.yml           text eol=lf
*.yaml          text eol=lf
*.md            text eol=lf
*.sh            text eol=lf
*.ps1           text eol=lf
*.dockerfile    text eol=lf
Dockerfile      text eol=lf
.env.example    text eol=lf

# Binary
*.png           binary
*.jpg           binary
*.jpeg          binary
*.gif           binary
*.webp          binary
*.ico           binary
*.woff2         binary
*.ttf           binary
*.eot           binary
*.otf           binary
'@ | Out-File -FilePath '.gitattributes' -Encoding utf8 -NoNewline

Step "5/8 - Staging all files"
git add -A

Step "6/8 - Creating initial commit"
git commit -m $InitialMessage --quiet
$head = (git rev-parse --short HEAD).Trim()
Write-Host "  commit: $head"

Step "7/8 - Adding remote 'origin'"
$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  origin already set to $existing"
} else {
    git remote add origin $RemoteUrl
    Write-Host "  origin -> $RemoteUrl"
}

Step "8/8 - Pushing to $DefaultBranch"
git push -u origin $DefaultBranch

Write-Host "`n✅ Repo is live at $RemoteUrl" -ForegroundColor Green
Write-Host "Next:"
Write-Host "  - Replace `<owner>` in README badges with your real GitHub org/user"
Write-Host "  - Enable branch protection on '$DefaultBranch' (require CI + 1 review)"
Write-Host "  - Optionally add release-please / semantic-release on merge"
