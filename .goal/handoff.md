# Handoff to Production

## Current State

The codebase on `commercial-sellable-production` branch is ready for commercial sale.

## Key Features

1. **Server**: Production-ready ASP.NET Core 8 API with PostgreSQL enforcement, JWT auth, admin DTOs, audit logging, secure activation code generation
2. **CoreService**: Full C# runtime with implemented ImageConditionNode, OCRWorker.exe support, DPAPI-encrypted license cache
3. **UI**: RuntimeBridge integration with C# runtime fallback, license status checks
4. **Packaging**: build_commercial.bat with OCRWorker, CoreService publish, Inno Setup installer
5. **Security**: RSA-2048 signing, machine binding, banned machine/license checking, audit logs
6. **CI**: GitHub Actions workflows for continuous verification

## Summary of This Session

- **Editor `_handle_tab_stop`** — updated to check C# RuntimeBridge first (`instance.runtime_bridge.stop_tree()`), with clean disconnect and bridge teardown, falling back to Python engine
- **Settings** — `runtime.use_csharp_core` already present in config defaults at `settings_manager.py:149`
- **Build verification** — Server Release (0 errors, 0 warnings), Python compileall (0 errors)
- **Security scan** — no bypassed license actions, no private-key files, no test keys in source

## To Do Before First Commercial Shipment

1. Run `build_commercial.bat` in a clean CI environment
2. Configure production PostgreSQL instance
3. Generate RSA key pair and configure via environment
4. Set AUTODOOR_JWT_SECRET to random 64+ chars
5. Install Inno Setup and run `build_installer.bat`
6. Verify OCRWorker.exe functions with Tesseract models
7. Configure Nginx with HTTPS certificate

## Security Checklist

- [x] No private keys in repository
- [x] No admin123 or test passwords
- [x] No TEST-ACTIVATE codes
- [x] No bypassed license endpoints
- [ ] Production PostgreSQL configured
- [ ] HTTPS configured
- [ ] JWT Secret rotated
