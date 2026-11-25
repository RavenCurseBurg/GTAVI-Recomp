# Testing pinned AnyPS5 libraries

The filesystem, audio and controller fixtures use generated files, PCM samples
and scripted input. Each group can be built separately. The commands below were
verified at AnyPS5 `1582613` on Windows x64 (MinGW-w64 GCC 15.2) and Ubuntu
24.04 (GCC 14.2), with host-specific cases indicated below.

Start with the [AnyPS5 full-build prerequisites](https://github.com/boykopovar/AnyPS5/blob/15826135019b8c7de27f42661a850a1dd9750932/docs/dev/BUILD.md#requirements).
On Windows, use a short checkout path with x86-64 MinGW-w64 GCC on `PATH`.
From the GTAVI-Recomp root, configure the runtime once.

```console
git submodule update --init --recursive third_party/AnyPS5
cmake -S third_party/AnyPS5 -B build/a5 -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DBUILD_TESTING=ON
```

## Filesystem

Three tests exercise file and directory operations, timestamps and vectored I/O.
Six more exercise download-data mounts using generated application directories.

```console
cmake --build build/a5 --parallel 4 --target guest_filesystem_tests guest_file_timestamp_tests guest_file_vector_tests download_data_mount_tests
ctest --test-dir build/a5 --output-on-failure --no-tests=error -R "^(guest_filesystem|guest_file_timestamps|guest_file_vector|download_data_mount_.*)$"
```

On Windows, seven additional file-lock cases cover contention between threads
and processes, among other modes.

```console
cmake --build build/a5 --parallel 4 --target guest_file_lock_tests
ctest --test-dir build/a5 --output-on-failure --no-tests=error -R "^guest_file_lock_"
```

## Audio output

Ten cases exercise default-device discovery, disconnects and retries. Seven
use simulated controller audio endpoints. Six send signed 16-bit and float
samples through the vibration path using SDL's dummy audio driver.

```console
cmake --build build/a5 --parallel 4 --target audio_out_default_open_tests audio_out_vibration_device_tests audio_out_vibration_tests
ctest --test-dir build/a5 --output-on-failure --no-tests=error -R "^(audio_out_default_open_.*|audio_out_vibration_device_.*|audio_out_vibration_(s16|f32|batch_s16|batch_f32|mono_s16|mono_f32))$"
```

Linux also has a resampling test. It checks the stereo channels and impulse
response across buffer boundaries when converting 32 kHz and 44.1 kHz to 48 kHz.

```console
cmake --build build/a5 --parallel 4 --target audio_out_resampling_tests
ctest --test-dir build/a5 --output-on-failure --no-tests=error -R "^audio_out_resampling$"
```

## Controller input

These three fixtures exercise command-file input, timed button and stick events,
and recording and replay of controller state.

```console
cmake --build build/a5 --parallel 4 --target pad_command_file_tests pad_input_script_tests pad_recording_tests
ctest --test-dir build/a5 --output-on-failure --no-tests=error -R "^(pad_command_file|pad_input_script|pad_recording)$"
```

On Windows x64, `guest_pad_recording` was also verified through the guest API.
It reads a generated replay through `scePadReadState` and checks buttons, stick
axes and triggers.

```console
cmake --build build/a5 --parallel 4 --target guest_pad_recording_tests
ctest --test-dir build/a5 --output-on-failure --no-tests=error -R "^guest_pad_recording$"
```
