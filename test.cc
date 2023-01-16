#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

namespace pb_data {

struct SubData {
  int64_t data;
};

struct Data {
  int32_t data1;
  std::vector<std::string> data2;
  std::map<std::string, SubData> data5;
};

struct Loader {
  Data d1;
  SubData d2;
};
} // namespace pb_data
