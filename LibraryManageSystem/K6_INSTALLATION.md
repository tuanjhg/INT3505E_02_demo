# k6 Installation Guide for Windows

## Quick Install (Recommended Method)

### Method 1: Using Chocolatey

If you have Chocolatey installed:

```powershell
choco install k6
```

### Method 2: Using winget

If you have winget (Windows Package Manager):

```powershell
winget install k6 --source winget
```

### Method 3: Manual Installation

1. Download the installer from: https://dl.k6.io/msi/k6-latest-amd64.msi
2. Run the downloaded MSI file
3. Follow the installation wizard
4. Restart PowerShell

## Verify Installation

```powershell
k6 version
```

You should see output like:
```
k6 v0.48.0 (2023-11-29T10:33:00+0000/v0.48.0-0-gabcdef, go1.21.4, windows/amd64)
```

## Troubleshooting

### k6 Command Not Found

After installation, if `k6` is not recognized:

1. **Close and reopen PowerShell**
2. **Check PATH environment variable:**
   ```powershell
   $env:Path -split ';' | Select-String k6
   ```
3. **Manually add to PATH if needed:**
   - Open "Edit the system environment variables"
   - Click "Environment Variables"
   - Find "Path" under "System variables"
   - Add: `C:\Program Files\k6`
   - Click OK and restart PowerShell

### Permission Denied

If you get permission errors:

```powershell
# Run PowerShell as Administrator
# Then install k6
choco install k6
```

## Next Steps

Once k6 is installed, you can:

1. **Run the load test:**
   ```powershell
   cd LibraryManageSystem
   .\run-k6-test.ps1
   ```

2. **Read the full guide:**
   - See [K6_LOAD_TESTING.md](./K6_LOAD_TESTING.md) for complete documentation

3. **Customize tests:**
   - Edit `load-test.js` to modify test scenarios

## Quick Test

Verify k6 works with a simple test:

```powershell
# Create a simple test file
@"
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const res = http.get('https://test.k6.io');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
"@ | Out-File -FilePath test.js -Encoding utf8

# Run it
k6 run test.js

# Clean up
Remove-Item test.js
```

If this works, k6 is properly installed!

## Additional Resources

- **k6 Official Website:** https://k6.io
- **k6 Documentation:** https://k6.io/docs
- **k6 Windows Installation:** https://k6.io/docs/get-started/installation/#windows
- **Chocolatey Package:** https://community.chocolatey.org/packages/k6
