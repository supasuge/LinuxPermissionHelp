# LinuxHelpers

Useful Python3 and bash scripts for getting information such as what aliases you have registered, as well as comprehensive permission quick-reference helpers.

If you choose to use any of these scripts, it's reccomended you place them within your local `$PATH` such as `/usr/local/bin/`

## permhelp.py

Similar to `perms` except quite a bit more comprehensive as far as showcasing examples.

---

## chmod-calc

This tool is based off of KickSecure's built-in tool `chmod-calc` but made better with prettier output (tabular).

Help menu:

```bash
usage: chmod-calc [-h] file

chmod‑calculator – display permissions, type and attributes of a file
using a tidy tabular layout.

positional arguments:
  file        Path to the file to analyze.

options:
  -h, --help  show this help message and exit
```

---

## catallx

- Full documentation can be found [here](https://github.com/supasuge/LinuxHelpers/tree/main/catallx)

---

## FileEnc-OpenSSL

Quick script I had written for experimental/learning purposes, **do not use it for encrypting data you legitamately intend to keep private**. There are a few issues within it and missing integrity verifications that a skilled attacked could exploit, or at the very least you data (or a *block* of it, could easily be corrupted via bit flips. With that out of the way, visit the URL below if you want to see the usage docs + script. It's perfectly useable, but after further analysis and critical thinking; it's certainly not ideal to say the least... but it does do the thing. So...

- Full documentation/usage can be found [here](https://github.com/supasuge/LinuxHelpers/blob/main/FileEnc-OpenSSL/README.md)
