#include "prx/libkernel/include/Api.hpp"
#include "prx/libkernel/File/include/File.hpp"

#include <cstdio>
#include <filesystem>
#include <string>
#ifdef _WIN32
#include <io.h>
#include <windows.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#endif

int main() {
    // The test runner gives each invocation an empty temporary directory.
    const std::filesystem::path path("ordinary.txt");
    const std::string native = path.string();
    std::FILE* stream = std::fopen(native.c_str(), "wb");
    if (!stream) return 1;
#ifdef _WIN32
    const int fd = _fileno(stream);
#else
    const int fd = fileno(stream);
#endif
    for (const bool use_fd : {false, true}) {
        for (const unsigned short mode : {0640, 0604, 0400, 0600}) {
            const int rc = use_fd ? sceKernelFchmod(fd, mode) : sceKernelChmod_nid_postfix(native.c_str(), mode);
            if (rc != 0) {
                std::fprintf(stderr, "%s mode=%04o failed: %d\n", use_fd ? "fd" : "path", mode, rc);
                return 2;
            }
#ifdef _WIN32
            const DWORD attributes = GetFileAttributesW(path.c_str());
            if (attributes == INVALID_FILE_ATTRIBUTES) return 3;
            const bool read_only = (attributes & FILE_ATTRIBUTE_READONLY) != 0;
            std::printf("%s requested=%04o host_readonly=%d\n", use_fd ? "fd" : "path", mode, read_only);
            if (read_only != ((mode & 0200) == 0)) return 4;
#else
            struct stat result{};
            if (stat(native.c_str(), &result) != 0) return 3;
            const unsigned int bits = result.st_mode & 0777;
            std::printf("%s requested=%04o host_mode=%04o\n", use_fd ? "fd" : "path", mode, bits);
            if (bits != mode) return 4;
#endif
        }
    }
    return std::fclose(stream) == 0 ? 0 : 5;
}
