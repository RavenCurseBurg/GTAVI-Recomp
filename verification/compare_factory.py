import statistics
import subprocess
import sys

paths = sys.argv[1:]
samples = {path: [] for path in paths}
for i in range(7):
    for path in (paths if i % 2 == 0 else reversed(paths)):
        samples[path].append(subprocess.check_output([path], text=True).split())
assert len({row[2] for runs in samples.values() for row in runs}) == 1
for path in paths:
    print(path, "median ns/construction", statistics.median(float(row[0]) for row in samples[path]),
          "allocations/construction", sorted({row[1] for row in samples[path]}))
assert max(float(row[1]) for row in samples[paths[1]]) < min(float(row[1]) for row in samples[paths[0]])
