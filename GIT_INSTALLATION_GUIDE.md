# Git Installation Guide for ESD Guidelines System

## Why Git is Needed

Git provides version control functionality for the ESD Guidelines system, allowing you to:
- Track changes to generated guidelines over time
- View history of document modifications
- Compare different versions of guidelines
- Maintain backup copies of all generated documents

## Git is Optional

**Important:** The system will work without Git! If you don't need version control features, you can skip Git installation. The system will:
- ✅ Generate guidelines normally
- ✅ Save files to disk
- ✅ Provide web interface
- ❌ No version history tracking
- ❌ No commit management

## Installing Git

### Windows

#### Option 1: Download from Official Website
1. Go to https://git-scm.com/downloads
2. Click "Download for Windows"
3. Run the downloaded installer
4. Follow the installation wizard (default settings are fine)
5. Restart your computer after installation

#### Option 2: Using Package Manager (if you have one)
```cmd
# Using Chocolatey
choco install git

# Using Winget (Windows 10/11)
winget install Git.Git

# Using Scoop
scoop install git
```

### macOS

#### Option 1: Using Homebrew (recommended)
```bash
brew install git
```

#### Option 2: Download from Official Website
1. Go to https://git-scm.com/downloads
2. Click "Download for macOS"
3. Run the downloaded installer

#### Option 3: Using Xcode Command Line Tools
```bash
xcode-select --install
```

### Linux

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install git
```

#### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install git

# Fedora
sudo dnf install git
```

#### Arch Linux
```bash
sudo pacman -S git
```

## Verifying Installation

After installation, verify Git is working:

1. Open a new command prompt/terminal
2. Run: `git --version`
3. You should see output like: `git version 2.x.x`

## Post-Installation Setup (Optional)

Configure your identity (recommended for better commit tracking):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Testing with ESD Guidelines System

After installing Git:

1. Close any running instances of the ESD Guidelines system
2. Navigate to your project directory
3. Run the test: `python test_system.py`
4. You should now see: ✅ Git is available and working

## Troubleshooting

### "git is not recognized" Error
- **Cause:** Git is not in your system PATH
- **Solution:** 
  1. Restart your command prompt/terminal
  2. If still not working, restart your computer
  3. If problem persists, reinstall Git and ensure "Add Git to PATH" is selected

### "Bad git executable" Error
- **Cause:** Git installation is incomplete or corrupted
- **Solution:** Reinstall Git from https://git-scm.com/downloads

### Permission Errors
- **Cause:** Insufficient permissions to create Git repository
- **Solution:** Run command prompt as Administrator (Windows) or use `sudo` (Linux/macOS)

## Alternative: Using System Without Git

If you can't install Git or prefer not to use version control:

1. The system works perfectly without Git
2. All features except version history will function normally
3. Generated guidelines are still saved to files
4. You can manually backup files if needed

## Need Help?

- Git Documentation: https://git-scm.com/doc
- Git Tutorial: https://git-scm.com/docs/gittutorial
- GitHub Git Handbook: https://guides.github.com/introduction/git-handbook/

---

**Note:** After installing Git, restart the ESD Guidelines system to enable version control features.
