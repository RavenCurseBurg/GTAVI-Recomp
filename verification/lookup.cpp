#include "gtavi/path.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <new>
#include <string>
#include <vector>

static std::size_t allocations = 0;
void* operator new(std::size_t size) {
    if (void* address = std::malloc(size == 0 ? 1 : size)) {
        ++allocations;
        return address;
    }
    throw std::bad_alloc{};
}
void operator delete(void* address) noexcept { std::free(address); }
void operator delete(void* address, std::size_t) noexcept { std::free(address); }

void measure(const char* name, const gtavi::DriveMap& map, const std::vector<std::string>& paths) {
    constexpr int repeats = 90000;
    std::size_t checksum = 0;
    const auto initial = allocations;
    const auto start = std::chrono::steady_clock::now();
    for (int i = 0; i < repeats; ++i) {
        for (const auto& path : paths) {
            const auto result = gtavi::posix_to_windows(path, map);
            if (!result) std::abort();
            checksum += result.value().size() + static_cast<unsigned char>(result.value().back());
        }
    }
    const auto elapsed = std::chrono::duration<double, std::nano>(std::chrono::steady_clock::now() - start).count();
    const auto count = allocations - initial;
    const double calls = static_cast<double>(repeats) * paths.size();
    std::cout << name << ' ' << elapsed / calls << ' ' << count / calls << ' ' << checksum << '\n';
}

template<class T> void print_result(const gtavi::Result<T>& result) {
    if (result) std::cout << "ok " << result.value() << '\n';
    else std::cout << "error " << result.error().describe() << '\n';
}

int main(int argc, char**) {
    const auto defaults = gtavi::DriveMap::default_map();
    const std::string base = "/media/workstation/archive";
    const auto custom = gtavi::DriveMap::with_mappings({
        {'D', base}, {'E', base + "/audio"}, {'S', base}, {'Z', "/"}
    });
    if (argc == 1) {
        measure("short", defaults, {"/mnt/c", "/mnt/d/x", "/mnt/f/maps/a", "/mnt/z/a.txt"});
        measure("long", defaults, {"/mnt/c/project/build/objects/part.obj", "/mnt/d/assets/audio/pcm.raw",
            "/mnt/f/" + std::string(160, 'a') + "/file.txt", "/mnt/z/images/material.dds"});
        measure("nested", custom, {base + "/audio/theme.wav", base + "//cache///models/mesh.bin/",
            base + "/docs/README.md", "/tmp/a.txt"});
        return 0;
    }
    const auto empty = gtavi::DriveMap::with_mappings({});
    for (const auto* map : {&defaults, &custom, &empty}) {
        for (const std::string& root : {std::string{}, std::string{"/"}, std::string{"//mnt"},
                                       std::string{"/mnt"}, base, base + "/audio", base + "/audio2"}) {
            for (const std::string& separator : std::vector<std::string>{"", "/", "//", "///"}) {
                for (const std::string& tail : std::vector<std::string>{"", "d", "d/", "Z", "audio/file.wav",
                                            "d/one//two/", "file with spaces", "x\\y", "./mesh", "../data", "\xc3\xa9/\xe9\x9f\xb3"}) {
                    const auto path = root + separator + tail;
                    print_result(map->drive_for(path));
                    print_result(gtavi::posix_to_windows(path, *map));
                }
            }
        }
    }
}
