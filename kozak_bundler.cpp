#include <iostream>
#include <fstream>
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
            size_t lastDot = p.find_last_of('.');
            
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
const std::string INTERPRETER_EXE = "main.exe";
const std::string OUTPUT_FOLDER = "build_exe";

// Markers
const std::string MARKER = "---KOZAK_PAYLOAD_START---";
const std::string SCRIPT_END = "---KOZAK_PAYLOAD_END---";
const std::string ASSET_START = "---ASSET_START---";
const std::string ASSET_END = "---ASSET_END---";
const std::string DATA_MANIFEST_START = "---DATA_MANIFEST_START---";
const std::string DATA_MANIFEST_END = "---DATA_MANIFEST_END---";

// ANSI Colors
namespace Color {
    const std::string RESET = "\033[0m";
    const std::string GREEN = "\033[92m";
    const std::string CYAN = "\033[96m";
    const std::string YELLOW = "\033[93m";
    const std::string RED = "\033[91m";
    const std::string BOLD = "\033[1m";
}

// Structure to hold bundling options
struct BundleOptions {
    std::string kozak_file;
    std::string icon_file;
    std::vector<std::pair<std::string, std::string>> add_data;
};

// Function to read entire file into a vector
std::vector<char> readBinaryFile(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary | std::ios::ate);
    if (!file) {
        throw std::runtime_error("Cannot open file: " + filename);
    }
    
    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);
    
    std::vector<char> buffer(size);
    if (!file.read(buffer.data(), size)) {
        throw std::runtime_error("Cannot read file: " + filename);
    }
    
    return buffer;
}

// Check for ResourceHacker installation
std::string findResourceHacker() {
    // Check common locations
    std::vector<std::string> possible_paths = {
        "ResourceHacker.exe",  // Same directory
        "C:\\Program Files (x86)\\Resource Hacker\\ResourceHacker.exe",
        "C:\\Program Files\\Resource Hacker\\ResourceHacker.exe",
        // Check PATH environment variable
    };
    
    for (const auto& path : possible_paths) {
        if (fs::exists(path)) {
            return path;
        }
    }
    
    return "";
}

bool applyIconWithResourceHacker(const std::string& exe_path, const std::string& icon_path, const std::string& rh_path) {
    std::cout << Color::CYAN << ">> Applying icon using ResourceHacker: " 
              << icon_path << Color::RESET << std::endl;
    
    // Create temp script for ResourceHacker
    std::string script_path = OUTPUT_FOLDER + "/_rh_script.txt";
    std::ofstream script(script_path);
    script << "[FILENAMES]\n";
    script << "Exe=" << exe_path << "\n";
    script << "SaveAs=" << exe_path << "\n";
    script << "Log=" << OUTPUT_FOLDER << "/_rh_log.txt\n";
    script << "[COMMANDS]\n";
    script << "-addoverwrite " << icon_path << ", ICONGROUP,MAINICON,0\n";
    script.close();
    
    // Execute ResourceHacker
    std::string cmd = rh_path + " -script \"" + script_path + "\"";
    
    std::cout << "  * Running ResourceHacker..." << std::endl;
    
    // Hide console window for ResourceHacker
    int result = system(cmd.c_str());
    
    // Clean up
    fs::remove(script_path);
    if (fs::exists(OUTPUT_FOLDER + "/_rh_log.txt")) {
        fs::remove(OUTPUT_FOLDER + "/_rh_log.txt");
    }
    
    if (result == 0) {
        std::cout << Color::GREEN << "[OK] Icon applied successfully!" << Color::RESET << std::endl;
        return true;
    } else {
        std::cout << Color::YELLOW << "[WARNING] ResourceHacker returned code: " << result << Color::RESET << std::endl;
        std::cout << "  Icon may not have been applied correctly" << std::endl;
        return false;
    }
}

void showIconHelp() {
    std::cout << "\n" << Color::CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << Color::RESET << std::endl;
    std::cout << Color::YELLOW << "  Icon Support: ResourceHacker Required" << Color::RESET << std::endl;
    std::cout << Color::CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << Color::RESET << std::endl;
    std::cout << "\nTo enable custom icon support:\n" << std::endl;
    std::cout << "1. Download ResourceHacker (FREE tool):" << std::endl;
    std::cout << Color::GREEN << "   http://www.angusj.com/resourcehacker/" << Color::RESET << std::endl;
    std::cout << "\n2. Install it, or place ResourceHacker.exe in:" << std::endl;
    std::cout << "   • Same folder as this bundler, OR" << std::endl;
    std::cout << "   • C:\\Program Files (x86)\\Resource Hacker\\" << std::endl;
    std::cout << "\n3. Run the bundler again with --icon flag" << std::endl;
    std::cout << "\n" << Color::YELLOW << "Note:" << Color::RESET << " ResourceHacker is a third-party tool by" << std::endl;
    std::cout << "Angus Johnson. KozakScript is not affiliated with it." << std::endl;
    std::cout << Color::CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << Color::RESET << std::endl;
}


// Function to write binary data to file
void writeBinaryFile(const std::string& filename, const std::vector<char>& data) {
    std::ofstream file(filename, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot write to file: " + filename);
    }
    file.write(data.data(), data.size());
}

// Function to append data to file
void appendToFile(const std::string& filename, const std::string& data) {
    std::ofstream file(filename, std::ios::binary | std::ios::app);
    if (!file) {
        throw std::runtime_error("Cannot append to file: " + filename);
    }
    file.write(data.c_str(), data.size());
}

void appendToFile(const std::string& filename, const std::vector<char>& data) {
    std::ofstream file(filename, std::ios::binary | std::ios::app);
    if (!file) {
        throw std::runtime_error("Cannot append to file: " + filename);
    }
    file.write(data.data(), data.size());
}

// Function to apply icon to executable using Windows API
bool applyIconNative(const std::string& exe_path, const std::string& icon_path) {
    std::cout << Color::CYAN << ">> Applying icon using native Windows API: " 
              << icon_path << Color::RESET << std::endl;
    
    // Convert to wide strings for Windows API
    int exe_len = MultiByteToWideChar(CP_UTF8, 0, exe_path.c_str(), -1, NULL, 0);
    int icon_len = MultiByteToWideChar(CP_UTF8, 0, icon_path.c_str(), -1, NULL, 0);
    
    std::vector<wchar_t> exe_wide(exe_len);
    std::vector<wchar_t> icon_wide(icon_len);
    
    MultiByteToWideChar(CP_UTF8, 0, exe_path.c_str(), -1, exe_wide.data(), exe_len);
    MultiByteToWideChar(CP_UTF8, 0, icon_path.c_str(), -1, icon_wide.data(), icon_len);
    
    // Load the icon file
    HANDLE hIcon = LoadImageW(NULL, icon_wide.data(), IMAGE_ICON, 0, 0, 
                              LR_LOADFROMFILE | LR_DEFAULTSIZE);
    
    if (!hIcon) {
        std::cout << Color::RED << "[ERROR] Failed to load icon file" << Color::RESET << std::endl;
        std::cout << "  * Error code: " << GetLastError() << std::endl;
        return false;
    }
    
    // Open the executable for resource update
    HANDLE hUpdate = BeginUpdateResourceW(exe_wide.data(), FALSE);
    if (!hUpdate) {
        std::cout << Color::RED << "[ERROR] Cannot open executable for update" << Color::RESET << std::endl;
        std::cout << "  * Error code: " << GetLastError() << std::endl;
        DestroyIcon((HICON)hIcon);
        return false;
    }
    
    // Read the .ico file to extract icon data
    std::ifstream ico_file(icon_path, std::ios::binary);
    if (!ico_file) {
        std::cout << Color::RED << "[ERROR] Cannot read icon file" << Color::RESET << std::endl;
        EndUpdateResourceW(hUpdate, TRUE);
        DestroyIcon((HICON)hIcon);
        return false;
    }
    
    // Read ICO header
    struct ICONDIR {
        WORD idReserved;
        WORD idType;
        WORD idCount;
    } icondir;
    
    ico_file.read((char*)&icondir, sizeof(ICONDIR));
    
    if (icondir.idReserved != 0 || icondir.idType != 1) {
        std::cout << Color::RED << "[ERROR] Invalid ICO file format" << Color::RESET << std::endl;
        EndUpdateResourceW(hUpdate, TRUE);
        DestroyIcon((HICON)hIcon);
        return false;
    }
    
    std::cout << "  * ICO contains " << icondir.idCount << " image(s)" << std::endl;
    
    // Read icon directory entries
    struct ICONDIRENTRY {
        BYTE bWidth;
        BYTE bHeight;
        BYTE bColorCount;
        BYTE bReserved;
        WORD wPlanes;
        WORD wBitCount;
        DWORD dwBytesInRes;
        DWORD dwImageOffset;
    };
    
    std::vector<ICONDIRENTRY> entries(icondir.idCount);
    ico_file.read((char*)entries.data(), sizeof(ICONDIRENTRY) * icondir.idCount);
    
    // Create icon group data
    struct GRPICONDIR {
        WORD idReserved;
        WORD idType;
        WORD idCount;
    };
    
    struct GRPICONDIRENTRY {
        BYTE bWidth;
        BYTE bHeight;
        BYTE bColorCount;
        BYTE bReserved;
        WORD wPlanes;
        WORD wBitCount;
        DWORD dwBytesInRes;
        WORD nID;
    };
    
    size_t group_size = sizeof(GRPICONDIR) + icondir.idCount * sizeof(GRPICONDIRENTRY);
    std::vector<BYTE> group_data(group_size);
    
    GRPICONDIR* pGroupDir = (GRPICONDIR*)group_data.data();
    pGroupDir->idReserved = 0;
    pGroupDir->idType = 1;
    pGroupDir->idCount = icondir.idCount;
    
    GRPICONDIRENTRY* pGroupEntries = (GRPICONDIRENTRY*)(group_data.data() + sizeof(GRPICONDIR));
    
    // Update individual icons and build group
    bool success = true;
    for (int i = 0; i < icondir.idCount; i++) {
        // Read icon image data
        ico_file.seekg(entries[i].dwImageOffset);
        std::vector<BYTE> icon_data(entries[i].dwBytesInRes);
        ico_file.read((char*)icon_data.data(), entries[i].dwBytesInRes);
        
        // Update icon resource (RT_ICON = 3)
        if (!UpdateResourceW(hUpdate, MAKEINTRESOURCEW(3), MAKEINTRESOURCEW(i + 1), 
                            MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL),
                            icon_data.data(), entries[i].dwBytesInRes)) {
            std::cout << Color::YELLOW << "[WARNING] Failed to update icon " << (i + 1) 
                      << Color::RESET << std::endl;
            success = false;
        }
        
        // Build group entry
        pGroupEntries[i].bWidth = entries[i].bWidth;
        pGroupEntries[i].bHeight = entries[i].bHeight;
        pGroupEntries[i].bColorCount = entries[i].bColorCount;
        pGroupEntries[i].bReserved = entries[i].bReserved;
        pGroupEntries[i].wPlanes = entries[i].wPlanes;
        pGroupEntries[i].wBitCount = entries[i].wBitCount;
        pGroupEntries[i].dwBytesInRes = entries[i].dwBytesInRes;
        pGroupEntries[i].nID = i + 1;
    }
    
    // Update icon group (RT_GROUP_ICON)
    if (!UpdateResourceW(hUpdate, MAKEINTRESOURCEW(14), MAKEINTRESOURCEW(1),
                    MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL),
                    group_data.data(), group_size)) {
    std::cout << Color::RED << "[ERROR] Failed to update icon group" << Color::RESET << std::endl;
    success = false;
}
    
    // Commit changes
    if (!EndUpdateResourceW(hUpdate, FALSE)) {
        std::cout << Color::RED << "[ERROR] Failed to commit resource updates" << Color::RESET << std::endl;
        DestroyIcon((HICON)hIcon);
        return false;
    }
    
    DestroyIcon((HICON)hIcon);
    
    if (success) {
        std::cout << Color::GREEN << "[OK] Icon applied successfully!" << Color::RESET << std::endl;
    }
    
    return success;
}

// Function to collect assets from .kozak file
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
        
        // Check for imports
        if (std::regex_search(line, match, import_pattern)) {
            std::string mod_name = match[2].str();
            
            if (fs::exists(mod_name + ".kozak")) {
                assets.push_back(mod_name + ".kozak");
            } else if (fs::exists(mod_name + ".koz")) {
                assets.push_back(mod_name + ".koz");
            } else if (fs::exists(mod_name)) {
                assets.push_back(mod_name);
            }
        }
        
        // Check for assets
        if (std::regex_search(line, match, asset_pattern)) {
            std::string asset_file = match[2].str();
            if (fs::exists(asset_file)) {
                assets.push_back(asset_file);
            }
        }
    }
    
    return assets;
}

// Function to convert number to string (for older compilers without std::to_string)
template<typename T>
std::string to_string(T value) {
    std::ostringstream oss;
    oss << value;
    return oss.str();
}

// Main bundling function
// BETTER STRATEGY: Never touch main.exe, work with a temp copy
bool bundle(const BundleOptions& options) {
    // Validate inputs
    if (!fs::exists(INTERPRETER_EXE)) {
        std::cout << Color::RED << "[ERROR] Interpreter not found at: " << INTERPRETER_EXE << Color::RESET << std::endl;
        return false;
    }
    
    if (!fs::exists(options.kozak_file)) {
        std::cout << Color::RED << "[ERROR] Script not found: " << options.kozak_file << Color::RESET << std::endl;
        return false;
    }
    
    // Check for ResourceHacker if icon requested
    std::string rh_path = "";
    bool has_icon_support = false;
    
    if (!options.icon_file.empty()) {
        rh_path = findResourceHacker();
        has_icon_support = !rh_path.empty();
        
        if (!has_icon_support) {
            showIconHelp();
            std::cout << "\n" << Color::YELLOW << "Continue bundling without icon? (y/n): " << Color::RESET;
            std::string response;
            std::getline(std::cin, response);
            if (response != "y" && response != "Y") {
                std::cout << Color::RED << "Bundling cancelled." << Color::RESET << std::endl;
                return false;
            }
        } else {
            std::cout << Color::GREEN << "✓ ResourceHacker found: " << rh_path << Color::RESET << std::endl;
        }
    }
    
    // Create output folder
    fs::create_directories(OUTPUT_FOLDER);
    
    std::string base_name = fs::path(options.kozak_file).stem();
    std::string output_exe = OUTPUT_FOLDER + "/" + base_name + ".exe";
    
    try {
        // Step 1: Copy interpreter
        std::cout << "\n" << Color::CYAN << ">> Step 1: Copying base interpreter..." << Color::RESET << std::endl;
        fs::copy_file(INTERPRETER_EXE, output_exe, fs::copy_options::overwrite_existing);
        std::cout << "  * Size: " << fs::file_size(output_exe) << " bytes" << std::endl;
        
        // Step 2: Embed main script
        std::cout << "\n" << Color::CYAN << ">> Step 2: Embedding script: " << options.kozak_file << Color::RESET << std::endl;
        appendToFile(output_exe, "\n" + MARKER + "\n");
        
        auto script_data = readBinaryFile(options.kozak_file);
        appendToFile(output_exe, script_data);
        
        appendToFile(output_exe, "\n" + SCRIPT_END + "\n");
        std::cout << "  * Script embedded" << std::endl;
        std::cout << "  * Size now: " << fs::file_size(output_exe) << " bytes" << std::endl;
        
        // Step 3: Embed assets
        auto assets = collectAssets(options.kozak_file);
        if (!assets.empty()) {
            std::cout << "\n" << Color::CYAN << ">> Step 3: Bundling " << assets.size() << " assets..." << Color::RESET << std::endl;
            
            for (size_t i = 0; i < assets.size(); i++) {
                std::cout << "  * " << assets[i] << std::endl;
                appendToFile(output_exe, "\n" + ASSET_START + "\n");
                
                auto asset_data = readBinaryFile(assets[i]);
                appendToFile(output_exe, asset_data);
                
                appendToFile(output_exe, "\n" + ASSET_END + "\n");
            }
            
            std::cout << "  * Assets bundled" << std::endl;
            std::cout << "  * Size now: " << fs::file_size(output_exe) << " bytes" << std::endl;
        }
        
        // Step 4: Embed additional data files
        if (!options.add_data.empty()) {
            std::cout << "\n" << Color::CYAN << ">> Step 4: Bundling " << options.add_data.size() 
                      << " additional data file(s)..." << Color::RESET << std::endl;
            
            std::string manifest = "[";
            bool first = true;
            
            for (size_t i = 0; i < options.add_data.size(); i++) {
                const std::string& src = options.add_data[i].first;
                const std::string& dst = options.add_data[i].second;
                
                if (!fs::exists(src)) {
                    std::cout << Color::YELLOW << "[WARNING] Data file not found: " << src << Color::RESET << std::endl;
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
            
            std::cout << "  * Data files bundled" << std::endl;
            std::cout << "  * Size now: " << fs::file_size(output_exe) << " bytes" << std::endl;
        }
        
        // Step 5: Apply icon if ResourceHacker is available
        if (!options.icon_file.empty() && has_icon_support && fs::exists(options.icon_file)) {
            std::cout << "\n" << Color::CYAN << ">> Step 5: Applying custom icon..." << Color::RESET << std::endl;
            
            if (applyIconWithResourceHacker(output_exe, options.icon_file, rh_path)) {
                std::cout << "  * Final size: " << fs::file_size(output_exe) << " bytes" << std::endl;
            } else {
                std::cout << Color::YELLOW << "  Executable created but icon may not be correct" << Color::RESET << std::endl;
            }
        }
        
        std::cout << "\n" << Color::GREEN << "[OK] Bundled successfully: " << Color::RESET << output_exe << std::endl;
        std::cout << "  * Final output size: " << fs::file_size(output_exe) << " bytes" << std::endl;
        
        if (!options.icon_file.empty() && !has_icon_support) {
            std::cout << "\n" << Color::YELLOW << "ℹ️  Tip: Install ResourceHacker to enable icon support" << Color::RESET << std::endl;
            std::cout << "   See: http://www.angusj.com/resourcehacker/" << std::endl;
        }
        
        return true;
        
    } catch (const std::exception& e) {
        std::cout << Color::RED << "[ERROR] " << e.what() << Color::RESET << std::endl;
        return false;
    }
}

void printUsage() {
    std::cout << Color::BOLD << Color::GREEN << "=====================================" << Color::RESET << std::endl;
    std::cout << Color::BOLD << Color::GREEN << "  KozakScript Bundler v6.0" << Color::RESET << std::endl;
    std::cout << Color::BOLD << Color::GREEN << "  With Optional Icon Support" << Color::RESET << std::endl;
    std::cout << Color::BOLD << Color::GREEN << "=====================================" << Color::RESET << std::endl;
    std::cout << std::endl;
    
    std::cout << Color::BOLD << "Usage:" << Color::RESET << std::endl;
    std::cout << "  kozak_bundler.exe <script.kozak> [options]" << std::endl;
    std::cout << std::endl;
    
    std::cout << Color::BOLD << "Options:" << Color::RESET << std::endl;
    std::cout << "  --icon <icon.ico>              Add custom icon (requires ResourceHacker)" << std::endl;
    std::cout << "  --add-data <src;dst>           Bundle additional data files" << std::endl;
    std::cout << std::endl;
    
    std::cout << Color::BOLD << "Icon Support:" << Color::RESET << std::endl;
    std::cout << "  To use --icon, install ResourceHacker from:" << std::endl;
    std::cout << "  " << Color::CYAN << "http://www.angusj.com/resourcehacker/" << Color::RESET << std::endl;
    std::cout << std::endl;
    
    std::cout << Color::BOLD << "Examples:" << Color::RESET << std::endl;
    std::cout << "  kozak_bundler.exe game.kozak" << std::endl;
    std::cout << "  kozak_bundler.exe game.kozak --icon icon.ico" << std::endl;
    std::cout << "  kozak_bundler.exe app.kozak --add-data config.txt;config.txt" << std::endl;
    std::cout << std::endl;
}


int main(int argc, char* argv[]) {
    // Enable UTF-8 console output
    SetConsoleOutputCP(CP_UTF8);
    
    if (argc < 2) {
        printUsage();
        return 1;
    }
    
    BundleOptions options;
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "--icon") {
            if (i + 1 < argc) {
                options.icon_file = argv[++i];
            } else {
                std::cout << Color::RED << "[ERROR] --icon requires a file path" << Color::RESET << std::endl;
                return 1;
            }
        } else if (arg == "--add-data") {
            if (i + 1 < argc) {
                std::string data_entry = argv[++i];
                size_t sep_pos = data_entry.find(';');
                
                if (sep_pos != std::string::npos) {
                    std::string src = data_entry.substr(0, sep_pos);
                    std::string dst = data_entry.substr(sep_pos + 1);
                    options.add_data.push_back(std::make_pair(src, dst));
                } else {
                    std::cout << Color::RED << "[ERROR] --add-data format: 'source;destination'" << Color::RESET << std::endl;
                    return 1;
                }
            } else {
                std::cout << Color::RED << "[ERROR] --add-data requires 'source;destination'" << Color::RESET << std::endl;
                return 1;
            }
        } else if (arg.find(".kozak") != std::string::npos || arg.find(".koz") != std::string::npos) {
            options.kozak_file = arg;
        } else {
            std::cout << Color::YELLOW << "[WARNING] Unknown argument: " << arg << Color::RESET << std::endl;
        }
    }
    
    if (options.kozak_file.empty()) {
        std::cout << Color::RED << "[ERROR] No .kozak file specified." << Color::RESET << std::endl;
        return 1;
    }
    
    bool success = bundle(options);
    
    if (success) {
        std::cout << "\n" << Color::GREEN << Color::BOLD << "=====================================" << Color::RESET << std::endl;
        std::cout << Color::GREEN << "SUCCESS: Bundling complete, Kozache!" << Color::RESET << std::endl;
        std::cout << Color::GREEN << Color::BOLD << "=====================================" << Color::RESET << std::endl;
        std::cout << "\n" << Color::CYAN << ">> Your executable is ready to distribute!" << Color::RESET << std::endl;
        std::cout << Color::CYAN << "   No external tools needed - all native!" << Color::RESET << std::endl;
        return 0;
    } else {
        std::cout << "\n" << Color::RED << "[ERROR] Bundling failed." << Color::RESET << std::endl;
        return 1;
    }
}