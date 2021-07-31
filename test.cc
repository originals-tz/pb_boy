#include <string>
#include <map>
#include <unordered_map>
#include <vector>
#include <set>

namespace pb_data
{


//! 单个机构持仓衍生数据
struct institem
{
    //! 持仓数量
    double m_num = 0;
    //! 持股占比
    double m_per = 0;
    //! 占比增减
    double m_change = 0;
    //! 解禁数量
    double m_free_num = 0;
    //! 解禁数量占比
    double m_free_per = 0;
    //! 是否新进入
    int32_t m_is_new = 0;
    //! 是否是连续增仓
    int32_t m_is_add = 0;
    //! 机构的持股市值
    double m_market_value = 0;
    //! 流通持股占比
    double m_float_per = 0;
    //! 流通持股占比增减
    double m_float_change = 0;
};

struct top10_shareholder
{
    int64_t m_time;
    float m_ratio;
};

struct instanalysis
{
    //! 时间
    uint64_t m_time;
    //! 总股本
    double m_shares;
    //! 当前价格
    double m_price;
    //! 是否已发布财报
    bool m_is_pub;
    //! 不同维度的机构数据
    std::vector<institem> m_insts;
};

struct investor_num
{
    //! 时间戳
    int64_t m_time;
    //! 散户人数
    int64_t m_investor_num;
    //! 户均持股
    double m_average_hold_num;
    //! 增减比例
    double m_zj_ratio;
    //! 季度增减比率
    double m_season_ratio;
    //! 是不是季度末
    bool m_isseason;
    //! 上个季度末的index
    int32_t m_last_season_index;
};

//个股持仓数据
struct StockHolder
{
     int64_t m_time;
    //! 披露日期
    int64_t m_pubtime;
    //! 个股代码
    std::string m_stock_code;
    //! 个股名称
    std::string m_stock_name;
    //! 板块名称
    std::string m_block_code;

    //! 持有A股数量
    int64_t m_ashare;
    //! 上一期持有A股的数量
    int64_t m_last_ashare;
    //! 持有无限售A股的数量
    int64_t m_nonresi_ashare;
    //! 解禁(+)/禁售(-)的数量
    double m_free_per_share;
    //! 占总股本比率
    double m_per_share;
    //! 上一期占总股本的比率
    double m_last_per_share;
    //! 占流通A股的比例
    double m_float_per_share;
    //! 上一期占流通A股的比例
    double m_last_float_per_share;

    //! 市值
    double m_market_value;
    //! 上一期的持仓市制
    double m_last_market_value;
    //! 基金代码
    std::string m_fund_code;
    //! 持有的基金数量
    int32_t m_hold_fund;
    //!总股本
    int64_t m_total_share;
    //!上期总股本
    int64_t m_last_total_share;
    //! 占净值比
    double m_nv;
    //! 上期占净值比
    double m_last_nv;
    //! 持有该个股的基金经理人数
    int64_t m_mgr_hold_count;
    //! 基金经理代码
    std::string m_personal_code;
    //! 公司名称
    std::string m_shlist;
};


struct instanalysis_season
{
    std::map<int64_t, instanalysis> m_season_data;
}

struct StarFundManager
{
    //! 基金经理名字
    std::string m_name;
    //! 基金经理代码
    std::string m_personal_code;
    //! 获奖次数
    int64_t m_awards_num = 0;
    //! 金牛奖
    int64_t m_golden_bull_num = 0;
    //! 明星基金奖
    int64_t m_star_fund_num = 0;
    //! 金基金将
    int64_t m_golden_fund_num = 0;
    //! 持有的基金
    std::set<std::string> m_funds;
};

struct router
{
    std::unordered_map<std::string, std::vector<top10_shareholder>> m_floatholder_top10_info;
    std::unordered_map<std::string, std::vector<instanalysis_season>> m_inst_analysis;
    std::unordered_map<std::string, std::vector<investor_num>> m_investor_num;
    std::map<std::string, std::vector<StockHolder>> m_star_mgr_stock_hold;
    std::map<std::string, std::vector<StockHolder>> m_stock_to_star_mgr;
    std::map<std::string, std::vector<StockHolder>> m_star_mgr_block_hold;
    std::set<std::string> m_star_mgr_personal_code_set;
    std::map<std::string, StarFundManager>> m_star_mgr_table;
};

}
