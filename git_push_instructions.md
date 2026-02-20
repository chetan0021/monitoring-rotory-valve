# Git Push Instructions

## Step-by-Step Guide to Push to GitHub

### 1. Configure Git (First Time Only)
```bash
git config --global user.name "chetan0021"
git config --global user.email "chetamv.kar@gmail.com"
```

### 2. Initialize Git Repository
```bash
git init
```

### 3. Add All Files
```bash
git add .
```

### 4. Create Initial Commit
```bash
git commit -m "Initial commit: Industrial Pressure Control System - Complete Implementation"
```

### 5. Add Remote Repository
```bash
git remote add origin https://github.com/chetan0021/monitoring-rotory-valve.git
```

### 6. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

---

## Alternative: If Repository Already Exists

If you get an error that the repository already has content:

```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

## Quick One-Line Commands

Run these commands in order:

```bash
git init
git add .
git commit -m "Complete implementation: Plant model, PID controller, closed-loop system, and analysis"
git remote add origin https://github.com/chetan0021/monitoring-rotory-valve.git
git branch -M main
git push -u origin main
```

---

## Verify Push

After pushing, visit:
https://github.com/chetan0021/monitoring-rotory-valve

---

## Troubleshooting

### If you get authentication errors:
1. Use GitHub Personal Access Token instead of password
2. Generate token at: https://github.com/settings/tokens
3. Use token as password when prompted

### If remote already exists:
```bash
git remote remove origin
git remote add origin https://github.com/chetan0021/monitoring-rotory-valve.git
```

### If you need to force push (use with caution):
```bash
git push -u origin main --force
```
