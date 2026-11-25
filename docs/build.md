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

To drive the toolchain yourself, note that the compiler is not on `PATH` by
default. Run the commands from a Developer PowerShell / Developer Command
Prompt, or initialise the environment first:

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
```

Then:

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

`gtavi-probe` prints host information and exercises path translation:

```console
$ gtavi-probe --to-posix "C:\Games\GTA VI\data" --to-windows /mnt/c/Games
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
gtavi-probe --mount D:/games --to-posix "D:\PS5\app0" --to-windows /games/PS5/app0
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

## Testing file operations in pinned AnyPS5

Use the [AnyPS5 full-build prerequisites](https://github.com/boykopovar/AnyPS5/blob/15826135019b8c7de27f42661a850a1dd9750932/docs/dev/BUILD.md#requirements)
for your host. On Windows, use a short checkout path and put the x86-64
MinGW-w64 GCC toolchain on `PATH`. Run the commands from the GTAVI-Recomp root.
The build targets four test programs and their dependencies.

```console
git submodule update --init --recursive third_party/AnyPS5
cmake -S third_party/AnyPS5 -B build/fs -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DBUILD_TESTING=ON
cmake --build build/fs --parallel 4 --target guest_filesystem_tests guest_file_timestamp_tests guest_file_vector_tests download_data_mount_tests
ctest --test-dir build/fs --output-on-failure --no-tests=error -R "^(guest_filesystem|guest_file_timestamps|guest_file_vector|download_data_mount_.*)$"
```

At `1582613`, these nine tests passed on Ubuntu 24.04 (GCC 14.2) and Windows
x64 (MinGW-w64 GCC 15.2). Three exercise file and directory operations,
timestamps, and vectored I/O. Six exercise download-data mounts using generated
application directories. The Windows build provides seven additional file-lock
cases, including contention between threads and processes.

```console
cmake --build build/fs --parallel 4 --target guest_file_lock_tests
ctest --test-dir build/fs --output-on-failure --no-tests=error -R "^guest_file_lock_"
```

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
