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
  std::map<int32_t, std::string> data3;
  std::map<int32_t, SubData> data4;
  std::map<std::string, SubData> data5;
};
} // namespace pb_data
