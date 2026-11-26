#include "gtavi/path.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <new>

std::size_t allocations = 0;
void* operator new(std::size_t n) {
    if (auto* p = std::malloc(n ? n : 1)) {
        ++allocations;
        return p;
    }
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

int main() {
    const auto reference = gtavi::DriveMap::default_map();
    if (reference.mappings().size() != 26) return 1;
    for (std::size_t i = 0; i < 26; ++i) {
        auto letter = static_cast<char>('A' + i);
        const auto path = std::string{"/mnt/"} + static_cast<char>('a' + i);
        const auto& entry = reference.mappings()[i];
        auto lookup = reference.mount_point_for(static_cast<char>('a' + i));
        auto drive = reference.drive_for(path + "/file");
        if (entry.drive != letter || entry.mount_point != path || !lookup || lookup.value() != path ||
            !drive || drive.value() != letter) return 2;
    }
    constexpr std::size_t repetitions = 200000;
    std::size_t checksum = 0;
    const auto start = std::chrono::steady_clock::now();
    const auto before = allocations;
    for (std::size_t i = 0; i < repetitions; ++i) {
        const auto map = gtavi::DriveMap::default_map();
        const auto& entry = map.mappings()[i % 26];
        checksum += static_cast<unsigned char>(entry.drive) + entry.mount_point.size();
    }
    const auto count = allocations - before;
    const auto elapsed = std::chrono::steady_clock::now() - start;
    std::cout << std::chrono::duration<double, std::nano>(elapsed).count()/repetitions << " "
              << static_cast<double>(count)/repetitions << " " << checksum << '\n';
}
