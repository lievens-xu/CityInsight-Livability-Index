# 数据字典

## 原始与参考输入

`data/raw/city_basic.csv`：`city_id`唯一正整数；`city_name`唯一城市名称；`province`省市；`region`区域；`city_level`行政类型。已统一为UTF-8带BOM。

`data/raw/data_source_tracking_2024.csv`：一行一个城市、年份、指标，三者唯一。

| 字段 | 定义 |
|---|---|
| indicator / category | 机器指标名 / 分类标签 |
| city / year | 城市名 / 数据所属年度，不是网页发布日期 |
| value / unit | 数值 / 标准单位；待采集值为空 |
| source_name / source_url / source_type | 来源名称 / 公开链接 / official或third_party |
| notes | 数据时点、统计口径、转换方法及待补原因 |
| verification_status / verified_on | verified或pending / 最近核对日期 |

`data/reference/ordinary_universities_2024.csv`：教育部普通高校名单八城287所子集。字段为`city_name`、`school_name`、`school_code`（10位字符串）、`education_level`（本科/专科）。按所在地聚合，不包含独立成人高校名单；截至2024-06-20。

`data/raw/city_indicators_2024.csv` 是早期六维设计模板，**不参与当前流程**。实际宽表由来源表生成：`city_indicators_2024_mvp.csv`。

## 实际宽表指标

| 字段 | 单位 | 方向 / 定义 |
|---|---|---|
| city_id / year | 编号 / 年 | 所有8城市都保留一行，包括无值城市 |
| gdp_per_capita | 元/人 | 正向；优先直接发布值，万元转元保留原精度 |
| avg_salary_non_private | 元/年 | 正向；单位从业/就业人员税前年平均工资，不能混用在岗职工工资 |
| avg_salary_private | 元/年 | 正向；单位从业/就业人员税前年平均工资 |
| tertiary_industry_ratio | % | 正向；0–100，不是0–1 |
| house_price | 元/平方米 | 负向；现有历史记录为2024年12月二手房挂牌均价，待复核 |
| avg_rent | 元/月 | 负向；待统一户型/面积及月份采集 |
| house_price_income_ratio_non_private | 年 | 负向；90平方米房价/非私营年工资，派生值 |
| house_price_income_ratio_private | 年 | 负向；90平方米房价/私营年工资，派生值 |
| hospital_count | 个 | 正向；全部医院，不使用医院+卫生院合计或仅综合医院 |
| university_count | 所 | 正向；教育部2024-06-20同一名单按所在地聚合 |
| metro_station_count | 个 | 正向；待统一换乘站是否去重 |
| pm25 | μg/m³ | 负向；年均值，监测范围见notes |
| good_air_days_ratio | % | 正向；年优良天比例，0–100 |
| park_count | 个 | 正向；公园存量，不使用年度新增数量 |

## 处理输出

`livability_scores_2024.csv`包含原始宽表字段及：

| 字段 | 定义 |
|---|---|
| city_name | 城市显示名 |
| economy_score / cost_score / service_score / environment_score | 共同指标的维度均分，0–100；未参与排名留空 |
| total_score / rank | 一位小数综合分 / 同年竞赛排名；未参与排名留空 |
| coverage / available_indicators | 12个原始指标的覆盖率（0–1） / 有值数量 |
| status | provisional或insufficient_data |
| {dimension}_available | 该城市该维度有值的候选指标数量（成本含派生比值），不一定都进入最终模型 |
| {indicator}_score | 实际进入共同指标模型的标准化分，未进入模型留空 |

`livability_scores_2024.metadata.json`记录权重、比较组城市ID及实际共同指标。`data_quality_2024.json`记录原始指标缺失数与覆盖率。`preference_scenarios_2024.csv`与`weight_sensitivity_2024.json`记录偏好场景与权重敏感性。

`dashboard/data/cities.json`与`cities.js`由同一CSV生成，严格将缺失值序列化为null，便于HTTP和离线页面读取。缺失数据不得替换为0。
