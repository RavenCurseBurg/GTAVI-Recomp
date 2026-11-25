# Building and testing

## Requirements

- CMake 3.21 or newer
- A C++20 compiler: MSVC 19.3x+, GCC 11+, or Clang 14+
- Ninja (recommended; used by the presets) or any generator CMake supports

No third-party libraries are required. The core library and the test suite use
only the C++ standard library.

## Windows

The quickest path is the helper script. It finds `vcvars64.bat` with `vswhere`,
so it works with any Visual Studio edition or the Build Tools, from any shell:

```bat
scripts\build-windows.bat              :: Release
scripts\build-windows.bat Debug        :: Debug
scripts\build-windows.bat Debug --clean
```

It configures with `-DGTAVI_WARNINGS_AS_ERRORS=ON`, so warnings fail locally the
same way they do in CI. It leaves the caller's environment unchanged.

To build with Ninja manually, open the **x64 Native Tools Command Prompt for VS**
from the Start menu. To use PowerShell, start `powershell` from that prompt so it
inherits the MSVC compiler and SDK environment. In either shell, change to the
repository root and run the following commands.

```powershell
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build --output-on-failure
```

Visual Studio's generator also works and does not need `vcvars64.bat`. Omit
`-G` to use whichever Visual Studio version is installed:

```powershell
cmake -S . -B build -A x64
cmake --build build --config Debug
ctest --test-dir build -C Debug --output-on-failure
```

## Linux

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build --output-on-failure
```

## Presets

`CMakePresets.json` defines `debug`, `release`, and `ci`:

```bash
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
```

The `ci` preset enables `-DGTAVI_WARNINGS_AS_ERRORS=ON`, matching the workflow in
`.github/workflows/ci.yml`. Builds must be warning-free with that setting.

## Options

| Option | Default | Purpose |
| --- | --- | --- |
| `GTAVI_BUILD_TESTS` | `ON` | Build the unit test suite |
| `GTAVI_BUILD_TOOLS` | `ON` | Build `gtavi-probe` |
| `GTAVI_WARNINGS_AS_ERRORS` | `OFF` | Treat warnings as errors |

## Running the diagnostic tool

`gtavi-probe` prints host information and exercises path translation. After the
manual Ninja build, run `./build/tools/gtavi_probe` from the repository root
in Bash or PowerShell. With the Visual Studio Debug build, use
`.\build\tools\Debug\gtavi_probe.exe`. For a preset or the Windows helper,
replace `build` with the build directory it used (such as `build/ci` or
`build/windows`).

```console
$ ./build/tools/gtavi_probe --to-posix "C:\Games\GTA VI\data" --to-windows /mnt/c/Games
gtavi-probe 0.1.0
platform:     windows
os version:   10.0.26200
architecture: x86_64
C:\Games\GTA VI\data -> /mnt/c/Games/GTA VI/data
/mnt/c/Games -> C:\Games
```

Use the repeatable `--mount` option to override a drive's default mount point.
The first override for each drive applies to every translation in the command.

```console
./build/tools/gtavi_probe --mount D:/games --to-posix "D:\PS5\app0" --to-windows /games/PS5/app0
```

Include its output when reporting platform-specific bugs.

## Checking a PS5 application directory

Python 3.11 or newer can check the readable input files before you run the relinker:

```console
python scripts/check_app0.py /path/to/app0 --title-id PPSA99999 --content-version 01.000.000
```

Use the application's own `sce_sys/param.json` and a readable ELF at `eboot.bin`.
Identity flags are optional. Use `--content-id` to distinguish packages that
share a title ID and version. Repeat `--module example.prx` to check explicitly named
shared modules under `sce_module/` in the same application directory. The JSON
report includes file hashes for valid inputs
and reports separate errors for missing or malformed files. The tool reads the
files in place. Passing the check confirms their structure and any requested
identity fields. Relinking and execution require further verification.

Run the generated-fixture tests with `python -I tests/test_check_app0.py`.

## Layout

```text
include/gtavi/      public headers
src/                portable implementation
src/platform/       per-OS implementation, selected by CMake only
tools/probe/        gtavi-probe diagnostic front end
tests/              unit tests and the minimal test framework
scripts/            helper build scripts
docs/               build notes, ADRs, research
cmake/              shared build configuration
```

Planned, created when the corresponding subsystem starts:

```text
src/loader/         guest executable loading
src/libraries/      translated PS5 library modules
```

Only `src/platform/` may contain OS-specific code. Everything else must compile
on both Windows and Linux, which the CI matrix enforces.

## Adding a test

Tests use a small in-repo framework, so no dependency is needed:

```cpp
#include "test_framework.h"

GTAVI_TEST(descriptive_name) {
    CHECK_TRUE(some_condition);
    CHECK_EQ(actual, expected);
}
```

Add the file to `tests/CMakeLists.txt`; registration is automatic.
