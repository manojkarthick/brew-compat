# brew-compat
* CLI tool to check homebrew formula compatibility for different macOS versions. 
* Supports core bottles and casks. Does not support taps (third-party repositories).

## Installation 
This tool has been built with python3. You need to install Python3.x for this utility.
Install this tool from PyPI (The Python Package Index) using pip:

```
❯ pip install brew-compat 
```

## Running

* Use `brew bundle dump` to generate the Brewfile
* Run `brew-compat` to check the compatibility status

## Options

* By default, compatibility is checked for Big Sur. Use `--macos-version` to change the macOS version to check against.
* You can use `--export` to export the results to CSV. It is written to a file called `compatibility.csv`
* Use `--verbose` to use verbose logging.

```
❯ brew-compat --help
usage: brew-compat [-h] [--macos-version {arm64_big_sur,big_sur,catalina,mojave,high_sierra,sierra,el_capitan}] [--verbose] [--export] [brewfile]

Check compatibility of brew formula against macOS versions

positional arguments:
  brewfile              Path to Brewfile

optional arguments:
  -h, --help            show this help message and exit
  --macos-version {arm64_big_sur,big_sur,catalina,mojave,high_sierra,sierra,el_capitan}
                        macOS version
  --verbose             Use verbose logging
  --export              Export results in CSV format

```

