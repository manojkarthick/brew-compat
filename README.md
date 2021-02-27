# brew-compat
* CLI tool to check homebrew formula compatibility for different macOS versions. 
* Supports core bottles and casks. Does not support taps (third-party repositories).

## Installation 
This tool has been built with python3. You need to install Python3.x for this utility.
Install this tool from PyPI (The Python Package Index) using pip:

```
❯ pip install brew-compat 
```

## Options

* By default, compatibility is checked for Big Sur. Use `--macos-version` to change the macOS version to check against.
* By default, looks for a brewfile in the current directory.  
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

## Running

* Use `brew bundle dump` to generate the Brewfile
* Run `brew-compat` to check the compatibility status

### Sample Output

```
❯ brew-compat
[2021-02-26 21:02:30,486] INFO - Using Brewfile: ~/code/brew-compat/Brewfile
[2021-02-26 21:02:30,486] INFO - Checking compatibility for big_sur
[2021-02-26 21:02:30,486] INFO - Getting details from Homebrew API for formulae, hold on...
+-------------+-------------------------+-------------+
| Kind        | Formula                 | Status      |
+-------------+-------------------------+-------------+
| Bottle      | direnv                  | Supported   |
| Bottle      | fzf                     | Supported   |
| Bottle      | sqlite                  | Supported   |
| Bottle      | goreleaser              | Supported   |
| Bottle      | helm                    | Supported   |
| Bottle      | kube-ps1                | No info     |
| Bottle      | simple-mtpfs            | Unsupported |
| Bottle      | smartmontools           | Supported   |
| Bottle      | terminal-notifier       | Supported   |
| Bottle      | tree                    | Supported   |
| Bottle      | wget                    | Supported   |
| Bottle      | xsv                     | Supported   |
| Bottle      | manojkarthick/pqrs/pqrs | Unknown     |
| Application | 1password               | Supported   |
| Application | balenaetcher            | No info     |
| Application | docker                  | No info     |
| Application | google-chrome           | No info     |
| Application | intel-power-gadget      | Supported   |
| Application | intellij-idea           | No info     |
| Application | iterm2                  | Supported   |
| Application | monitorcontrol          | Supported   |
+-------------+-------------------------+-------------+
```
