# Migrating to UV Package Manager

If you already have the ESD & Latchup Guidelines Generator installed and want to switch to using UV for better performance, follow these simple steps:

## Windows Users

1. **Run the setup script:**
   ```cmd
   setup_uv.bat
   ```
   This will install UV and reinstall all dependencies.

2. **That's it!** The start scripts will now automatically use UV.

## Linux/Mac Users

1. **Make the setup script executable:**
   ```bash
   chmod +x setup_uv.sh
   ```

2. **Run the setup script:**
   ```bash
   ./setup_uv.sh
   ```

3. **Done!** The system will now use UV for all package operations.

## Manual Migration

If you prefer to migrate manually:

```bash
# Install UV
pip install uv

# Reinstall all packages with UV (in your virtual environment)
uv pip install -r requirements.txt --force-reinstall
```

## Verification

To verify UV is installed correctly:

```bash
uv --version
```

You should see the UV version information.

## Rollback

If you need to switch back to standard pip, simply use pip commands instead of uv:
- Replace `uv pip install` with `pip install`
- All scripts will continue to work

## Benefits You'll See

- ⚡ Package installation 10-100x faster
- 🔄 Better dependency resolution
- 💾 Reduced disk usage (global package cache)
- 🚀 Faster CI/CD builds

No other changes are needed - UV is a drop-in replacement for pip!
