#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <regex>
#include <cstring>
#include <windows.h>
#include <sys/stat.h>
#include <direct.h>

// Simple filesystem replacement for older compilers
namespace fs {
    inline bool exists(const std::string& path) {
        struct stat buffer;
        return (stat(path.c_str(), &buffer) == 0);
    }

    inline void create_directories(const std::string& path) {
        _mkdir(path.c_str());
    }

    inline size_t file_size(const std::string& path) {
        struct stat stat_buf;
        int rc = stat(path.c_str(), &stat_buf);
        return rc == 0 ? stat_buf.st_size : 0;
    }

    inline void copy_file(const std::string& from, const std::string& to, int options = 0) {
        std::ifstream src(from, std::ios::binary);
        std::ofstream dst(to, std::ios::binary | std::ios::trunc);
        if (!src || !dst) {
            throw std::runtime_error("Cannot copy file");
        }
        dst << src.rdbuf();
    }

    inline void remove(const std::string& path) {
        ::remove(path.c_str());
    }

    class path {
        std::string p;
    public:
        path(const std::string& s) : p(s) {}

        std::string stem() const {
            size_t lastSlash = p.find_last_of("/\\");
            size_t lastDot   = p.find_last_of('.');
            std::string filename = (lastSlash == std::string::npos) ? p : p.substr(lastSlash + 1);
            if (lastDot != std::string::npos && lastDot > (lastSlash == std::string::npos ? 0 : lastSlash)) {
                size_t start = (lastSlash == std::string::npos) ? 0 : lastSlash + 1;
                return p.substr(start, lastDot - start);
            }
            return filename;
        }

        std::string string() const { return p; }
    };

    enum copy_options { overwrite_existing = 1 };
}

// Configuration
const std::string INTERPRETER_EXE  = "KozakScript.exe";
const std::string OUTPUT_FOLDER    = "build_exe";

// Markers
const std::string MARKER              = "---KOZAK_PAYLOAD_START---";
const std::string SCRIPT_END          = "---KOZAK_PAYLOAD_END---";
const std::string ASSET_START         = "---ASSET_START---";
const std::string ASSET_END           = "---ASSET_END---";
const std::string DATA_MANIFEST_START = "---DATA_MANIFEST_START---";
const std::string DATA_MANIFEST_END   = "---DATA_MANIFEST_END---";

// ANSI Colors
namespace Color {
    const std::string RESET  = "\033[0m";
    const std::string GREEN  = "\033[92m";
    const std::string CYAN   = "\033[96m";
    const std::string YELLOW = "\033[93m";
    const std::string RED    = "\033[91m";
    const std::string BOLD   = "\033[1m";
}

// Structure to hold bundling options
struct BundleOptions {
    std::string kozak_file;
    std::string icon_file;
    std::vector<std::pair<std::string, std::string>> add_data;
};

// Read entire file into a vector
std::vector<char> readBinaryFile(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary | std::ios::ate);
    if (!file) throw std::runtime_error("Cannot open file: " + filename);
    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<char> buffer(size);
    if (!file.read(buffer.data(), size)) throw std::runtime_error("Cannot read file: " + filename);
    return buffer;
}

// Append data to file
void appendToFile(const std::string& filename, const std::string& data) {
    std::ofstream file(filename, std::ios::binary | std::ios::app);
    if (!file) throw std::runtime_error("Cannot append to file: " + filename);
    file.write(data.c_str(), data.size());
}

void appendToFile(const std::string& filename, const std::vector<char>& data) {
    std::ofstream file(filename, std::ios::binary | std::ios::app);
    if (!file) throw std::runtime_error("Cannot append to file: " + filename);
    file.write(data.data(), data.size());
}

// ---------------------------------------------------------------------------
// Find the true end of the PE image by walking section headers.
// Everything after this offset is "appended data" (PyInstaller ZIP, our
// KOZAK payload, etc.) that the resource API must never see or touch.
// ---------------------------------------------------------------------------
size_t getPEEndOffset(const std::vector<char>& data) {
    if (data.size() < sizeof(IMAGE_DOS_HEADER)) return 0;

    const IMAGE_DOS_HEADER* dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(data.data());
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return 0;

    DWORD pe_offset = dos->e_lfanew;
    if (pe_offset + sizeof(IMAGE_NT_HEADERS32) > data.size()) return 0;

    const IMAGE_NT_HEADERS32* nt = reinterpret_cast<const IMAGE_NT_HEADERS32*>(data.data() + pe_offset);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return 0;

    WORD num_sections  = nt->FileHeader.NumberOfSections;
    WORD opt_hdr_size  = nt->FileHeader.SizeOfOptionalHeader;

    size_t section_table_offset = pe_offset + 4 + sizeof(IMAGE_FILE_HEADER) + opt_hdr_size;
    if (section_table_offset + num_sections * sizeof(IMAGE_SECTION_HEADER) > data.size()) return 0;

    size_t pe_end = 0;
    for (int i = 0; i < num_sections; i++) {
        const IMAGE_SECTION_HEADER* sec = reinterpret_cast<const IMAGE_SECTION_HEADER*>(
            data.data() + section_table_offset + i * sizeof(IMAGE_SECTION_HEADER));
        if (sec->PointerToRawData == 0 || sec->SizeOfRawData == 0) continue;
        size_t end = (size_t)sec->PointerToRawData + (size_t)sec->SizeOfRawData;
        if (end > pe_end) pe_end = end;
    }

    return pe_end;
}

// ---------------------------------------------------------------------------
// Apply icon using Win32 resource API only — no external tools required.
//
// PyInstaller one-file exes append a large ZIP archive after the real PE.
// EndUpdateResourceW truncates anything after the last known section, which
// destroys that ZIP and breaks the exe.  The fix:
//   1. Read the exe, locate true PE end via section headers.
//   2. Save everything after the PE as `tail_payload`.
//   3. Truncate the file to the clean PE.
//   4. Let BeginUpdateResource / EndUpdateResource work on the clean PE.
//   5. Re-append `tail_payload` so the exe is whole again.
// ---------------------------------------------------------------------------
bool applyIconNative(const std::string& exe_path, const std::string& icon_path) {
    std::cout << Color::CYAN << ">> Applying icon using native Windows API: "
              << icon_path << Color::RESET << std::endl;

    // 1. Read exe and find where the PE proper ends
    std::vector<char> exe_data = readBinaryFile(exe_path);
    size_t pe_end = getPEEndOffset(exe_data);

    std::vector<char> tail_payload;
    if (pe_end > 0 && pe_end < exe_data.size()) {
        tail_payload.assign(exe_data.begin() + pe_end, exe_data.end());
        std::cout << "  * PE ends at byte " << pe_end
                  << " — saving " << tail_payload.size() << " bytes of appended payload" << std::endl;

        // Truncate to clean PE
        std::ofstream trunc(exe_path, std::ios::binary | std::ios::trunc);
        if (!trunc) {
            std::cout << Color::RED << "[ERROR] Cannot truncate exe for icon patching" << Color::RESET << std::endl;
            return false;
        }
        trunc.write(exe_data.data(), pe_end);
        trunc.close();
    } else {
        std::cout << "  * No payload tail detected — treating as standard PE" << std::endl;
    }

    // 2. Wide-string paths for Win32
    int exe_wlen  = MultiByteToWideChar(CP_UTF8, 0, exe_path.c_str(),  -1, NULL, 0);
    int icon_wlen = MultiByteToWideChar(CP_UTF8, 0, icon_path.c_str(), -1, NULL, 0);
    std::vector<wchar_t> exe_wide(exe_wlen), icon_wide(icon_wlen);
    MultiByteToWideChar(CP_UTF8, 0, exe_path.c_str(),  -1, exe_wide.data(),  exe_wlen);
    MultiByteToWideChar(CP_UTF8, 0, icon_path.c_str(), -1, icon_wide.data(), icon_wlen);

    // 3. Read .ico
    std::ifstream ico(icon_path, std::ios::binary);
    if (!ico) {
        std::cout << Color::RED << "[ERROR] Cannot read icon file" << Color::RESET << std::endl;
        return false;
    }

#pragma pack(push, 1)
    struct ICONDIR        { WORD idReserved, idType, idCount; };
    struct ICONDIRENTRY   { BYTE bWidth, bHeight, bColorCount, bReserved;
                            WORD wPlanes, wBitCount; DWORD dwBytesInRes, dwImageOffset; };
    struct GRPICONDIR     { WORD idReserved, idType, idCount; };
    struct GRPICONDIRENTRY{ BYTE bWidth, bHeight, bColorCount, bReserved;
                            WORD wPlanes, wBitCount; DWORD dwBytesInRes; WORD nID; };
#pragma pack(pop)

    ICONDIR icondir;
    ico.read((char*)&icondir, sizeof(ICONDIR));
    if (icondir.idReserved != 0 || icondir.idType != 1) {
        std::cout << Color::RED << "[ERROR] Invalid ICO file format" << Color::RESET << std::endl;
        return false;
    }
    std::cout << "  * ICO contains " << icondir.idCount << " image(s)" << std::endl;

    std::vector<ICONDIRENTRY> entries(icondir.idCount);
    ico.read((char*)entries.data(), sizeof(ICONDIRENTRY) * icondir.idCount);

    // 4. Build RT_GROUP_ICON blob
    size_t group_size = sizeof(GRPICONDIR) + icondir.idCount * sizeof(GRPICONDIRENTRY);
    std::vector<BYTE> group_data(group_size);
    GRPICONDIR* pGD = (GRPICONDIR*)group_data.data();
    pGD->idReserved = 0; pGD->idType = 1; pGD->idCount = icondir.idCount;
    GRPICONDIRENTRY* pGE = (GRPICONDIRENTRY*)(group_data.data() + sizeof(GRPICONDIR));

    // 5. Open exe for resource update
    HANDLE hUpdate = BeginUpdateResourceW(exe_wide.data(), FALSE);
    if (!hUpdate) {
        std::cout << Color::RED << "[ERROR] BeginUpdateResourceW failed (code "
                  << GetLastError() << ")" << Color::RESET << std::endl;
        // Restore payload before bailing
        if (!tail_payload.empty()) {
            std::ofstream restore(exe_path, std::ios::binary | std::ios::app);
            restore.write(tail_payload.data(), tail_payload.size());
        }
        return false;
    }

    bool success = true;

    for (int i = 0; i < icondir.idCount; i++) {
        ico.seekg(entries[i].dwImageOffset);
        std::vector<BYTE> img(entries[i].dwBytesInRes);
        ico.read((char*)img.data(), entries[i].dwBytesInRes);

        if (!UpdateResourceW(hUpdate, MAKEINTRESOURCEW(3), MAKEINTRESOURCEW(i + 1),
                             MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL),
                             img.data(), entries[i].dwBytesInRes)) {
            std::cout << Color::YELLOW << "[WARNING] Failed to write RT_ICON " << (i+1) << Color::RESET << std::endl;
            success = false;
        }

        pGE[i] = { entries[i].bWidth, entries[i].bHeight, entries[i].bColorCount,
                   entries[i].bReserved, entries[i].wPlanes, entries[i].wBitCount,
                   entries[i].dwBytesInRes, (WORD)(i + 1) };
    }

    if (!UpdateResourceW(hUpdate, MAKEINTRESOURCEW(14), MAKEINTRESOURCEW(1),
                         MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL),
                         group_data.data(), (DWORD)group_size)) {
        std::cout << Color::RED << "[ERROR] Failed to write RT_GROUP_ICON" << Color::RESET << std::endl;
        success = false;
    }

    if (!EndUpdateResourceW(hUpdate, FALSE)) {
        std::cout << Color::RED << "[ERROR] EndUpdateResourceW failed (code "
                  << GetLastError() << ")" << Color::RESET << std::endl;
        success = false;
    }

    // 6. Re-append the saved tail
    if (!tail_payload.empty()) {
        std::ofstream restore(exe_path, std::ios::binary | std::ios::app);
        if (!restore) {
            std::cout << Color::RED << "[ERROR] Could not re-append payload — exe may be corrupt!" << Color::RESET << std::endl;
            return false;
        }
        restore.write(tail_payload.data(), tail_payload.size());
        std::cout << "  * Payload re-appended (" << tail_payload.size() << " bytes)" << std::endl;
    }

    if (success)
        std::cout << Color::GREEN << "[OK] Icon applied successfully!" << Color::RESET << std::endl;

    return success;
}

// Collect assets referenced by a .kozak script
std::vector<std::string> collectAssets(const std::string& kozak_file) {
    std::vector<std::string> assets;
    std::ifstream file(kozak_file);
    if (!file) {
        std::cout << Color::YELLOW << "[WARNING] Could not scan for assets" << Color::RESET << std::endl;
        return assets;
    }

    std::regex import_pattern(R"((Importuvaty|Import|Importirovat)\s*\(\s*[\"']([^\"']+)[\"']\s*\))");
    std::regex asset_pattern(R"((sound|sprite)\s*\(\s*[\"']([^\"']+)[\"']\s*\))", std::regex::icase);

    std::string line;
    while (std::getline(file, line)) {
        std::smatch match;
        if (std::regex_search(line, match, import_pattern)) {
            std::string m = match[2].str();
            if      (fs::exists(m + ".kozak")) assets.push_back(m + ".kozak");
            else if (fs::exists(m + ".koz"))   assets.push_back(m + ".koz");
            else if (fs::exists(m))            assets.push_back(m);
        }
        if (std::regex_search(line, match, asset_pattern)) {
            std::string a = match[2].str();
            if (fs::exists(a)) assets.push_back(a);
        }
    }
    return assets;
}

// Main bundling function
bool bundle(const BundleOptions& options) {
    if (!fs::exists(INTERPRETER_EXE)) {
        std::cout << Color::RED << "[ERROR] Interpreter not found: " << INTERPRETER_EXE << Color::RESET << std::endl;
        return false;
    }
    if (!fs::exists(options.kozak_file)) {
        std::cout << Color::RED << "[ERROR] Script not found: " << options.kozak_file << Color::RESET << std::endl;
        return false;
    }
    if (!options.icon_file.empty() && !fs::exists(options.icon_file)) {
        std::cout << Color::RED << "[ERROR] Icon file not found: " << options.icon_file << Color::RESET << std::endl;
        return false;
    }

    fs::create_directories(OUTPUT_FOLDER);
    std::string base_name  = fs::path(options.kozak_file).stem();
    std::string output_exe = OUTPUT_FOLDER + "/" + base_name + ".exe";

    try {
        // Step 1: Copy interpreter
        std::cout << "\n" << Color::CYAN << ">> Step 1: Copying base interpreter..." << Color::RESET << std::endl;
        fs::copy_file(INTERPRETER_EXE, output_exe, fs::copy_options::overwrite_existing);
        std::cout << "  * Size: " << fs::file_size(output_exe) << " bytes" << std::endl;

        // Step 2: Apply icon.
        // applyIconNative saves/restores any PE tail automatically, so the
        // order relative to payload appending no longer matters — but doing
        // it early keeps things clean.
        if (!options.icon_file.empty()) {
            std::cout << "\n" << Color::CYAN << ">> Step 2: Applying custom icon..." << Color::RESET << std::endl;
            if (!applyIconNative(output_exe, options.icon_file)) {
                std::cout << Color::YELLOW << "  Icon not applied — continuing without it." << Color::RESET << std::endl;
            } else {
                std::cout << "  * Size after icon: " << fs::file_size(output_exe) << " bytes" << std::endl;
            }
        }

        // Step 3: Embed main script
        std::cout << "\n" << Color::CYAN << ">> Step 3: Embedding script: " << options.kozak_file << Color::RESET << std::endl;
        appendToFile(output_exe, "\n" + MARKER + "\n");
        appendToFile(output_exe, readBinaryFile(options.kozak_file));
        appendToFile(output_exe, "\n" + SCRIPT_END + "\n");
        std::cout << "  * Script embedded" << std::endl;
        std::cout << "  * Size now: " << fs::file_size(output_exe) << " bytes" << std::endl;

        // Step 4: Embed assets
        auto assets = collectAssets(options.kozak_file);
        if (!assets.empty()) {
            std::cout << "\n" << Color::CYAN << ">> Step 4: Bundling " << assets.size() << " asset(s)..." << Color::RESET << std::endl;
            for (auto& a : assets) {
                std::cout << "  * " << a << std::endl;
                appendToFile(output_exe, "\n" + ASSET_START + "\n");
                appendToFile(output_exe, readBinaryFile(a));
                appendToFile(output_exe, "\n" + ASSET_END + "\n");
            }
            std::cout << "  * Size now: " << fs::file_size(output_exe) << " bytes" << std::endl;
        }

        // Step 5: Embed additional data files
        if (!options.add_data.empty()) {
            std::cout << "\n" << Color::CYAN << ">> Step 5: Bundling " << options.add_data.size()
                      << " data file(s)..." << Color::RESET << std::endl;

            std::string manifest = "[";
            bool first = true;

            for (auto& kv : options.add_data) {
                const std::string& src = kv.first;
                const std::string& dst = kv.second;
                if (!fs::exists(src)) {
                    std::cout << Color::YELLOW << "[WARNING] Not found: " << src << Color::RESET << std::endl;
                    continue;
                }
                std::cout << "  * " << src << " -> " << dst << std::endl;
                auto content = readBinaryFile(src);
                if (!first) manifest += ",";
                std::ostringstream oss;
                oss << "\n  {\"destination\":\"" << dst << "\",\"size\":" << content.size()
                    << ",\"original\":\"" << src << "\"}";
                manifest += oss.str();
                first = false;
                appendToFile(output_exe, "\n---DATA_FILE_START---\n");
                appendToFile(output_exe, content);
                appendToFile(output_exe, "\n---DATA_FILE_END---\n");
            }

            manifest += "\n]";
            appendToFile(output_exe, "\n" + DATA_MANIFEST_START + "\n");
            appendToFile(output_exe, manifest);
            appendToFile(output_exe, "\n" + DATA_MANIFEST_END + "\n");
            std::cout << "  * Size now: " << fs::file_size(output_exe) << " bytes" << std::endl;
        }

        std::cout << "\n" << Color::GREEN << "[OK] Bundled successfully: " << Color::RESET << output_exe << std::endl;
        std::cout << "  * Final size: " << fs::file_size(output_exe) << " bytes" << std::endl;
        return true;

    } catch (const std::exception& e) {
        std::cout << Color::RED << "[ERROR] " << e.what() << Color::RESET << std::endl;
        return false;
    }
}

void printUsage() {
    std::cout << Color::BOLD << Color::GREEN << "=====================================" << Color::RESET << "\n";
    std::cout << Color::BOLD << Color::GREEN << "  KozakScript Bundler v6.0"           << Color::RESET << "\n";
    std::cout << Color::BOLD << Color::GREEN << "=====================================" << Color::RESET << "\n\n";
    std::cout << Color::BOLD << "Usage:\n" << Color::RESET;
    std::cout << "  kozak_bundler.exe <script.kozak> [options]\n\n";
    std::cout << Color::BOLD << "Options:\n" << Color::RESET;
    std::cout << "  --icon <icon.ico>          Add custom icon (.ico format)\n";
    std::cout << "  --add-data <src;dst>       Bundle additional data files\n\n";
    std::cout << Color::BOLD << "Examples:\n" << Color::RESET;
    std::cout << "  kozak_bundler.exe game.kozak\n";
    std::cout << "  kozak_bundler.exe game.kozak --icon icon.ico\n";
    std::cout << "  kozak_bundler.exe app.kozak --add-data config.txt;config.txt\n\n";
}

int main(int argc, char* argv[]) {
    SetConsoleOutputCP(CP_UTF8);

    if (argc < 2) { printUsage(); return 1; }

    BundleOptions options;

    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];

        if (arg == "--icon") {
            if (i + 1 < argc) options.icon_file = argv[++i];
            else { std::cout << Color::RED << "[ERROR] --icon requires a path\n" << Color::RESET; return 1; }
        } else if (arg == "--add-data") {
            if (i + 1 < argc) {
                std::string entry = argv[++i];
                size_t sep = entry.find(';');
                if (sep != std::string::npos)
                    options.add_data.push_back({ entry.substr(0, sep), entry.substr(sep + 1) });
                else { std::cout << Color::RED << "[ERROR] --add-data format: source;dest\n" << Color::RESET; return 1; }
            } else { std::cout << Color::RED << "[ERROR] --add-data requires source;dest\n" << Color::RESET; return 1; }
        } else if (arg.find(".kozak") != std::string::npos || arg.find(".koz") != std::string::npos) {
            options.kozak_file = arg;
        } else {
            std::cout << Color::YELLOW << "[WARNING] Unknown argument: " << arg << Color::RESET << std::endl;
        }
    }

    if (options.kozak_file.empty()) {
        std::cout << Color::RED << "[ERROR] No .kozak file specified.\n" << Color::RESET;
        return 1;
    }

    if (bundle(options)) {
        std::cout << "\n" << Color::GREEN << Color::BOLD << "=====================================\n" << Color::RESET;
        std::cout << Color::GREEN << "SUCCESS: Bundling complete, Kozache!\n" << Color::RESET;
        std::cout << Color::GREEN << Color::BOLD << "=====================================\n" << Color::RESET;
        std::cout << "\n" << Color::CYAN << ">> Your executable is ready to distribute!\n" << Color::RESET;
        std::cout << Color::CYAN << "   No external tools needed - all native!\n" << Color::RESET;
        return 0;
    }

    std::cout << "\n" << Color::RED << "[ERROR] Bundling failed.\n" << Color::RESET;
    return 1;
}
