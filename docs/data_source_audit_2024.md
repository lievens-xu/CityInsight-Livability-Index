# 2024 数据来源与口径审计

复核日期：2026-10-10。数据所属年度为2024，不因2025或2026年的网页发布时间而改变。完整字段、数值、精确URL和复核状态保存在 `data/raw/data_source_tracking_2024.csv`，看板可直接查询。

## 原三城更正

| 项目 | 原值/做法 | 当前值/做法 | 依据 |
|---|---|---|---|
| 上海人均GDP | 217424，按年末人口估算 | 217100，直接发布21.71万元转元 | [上海统计年鉴2025 表1.5](https://tjj.sh.gov.cn/tjnj/2025tjnj/C01/C0105B.htm) |
| 南京人均GDP | 193180，按年末人口估算 | 193483，直接发布值 | [南京2024统计公报](https://tjj.nanjing.gov.cn/njstjj/202504/t20250401_5108470.html) |
| 苏州非私营工资 | 在岗职工143611 | 从业人员141827 | [苏州统计局问答](https://tjj.suzhou.gov.cn/sztjj/rdwd/202506/1e244bbcb19c4036922eb1c25f4991e1.shtml) |
| 南京非私营工资 | 在岗职工165726 | 从业人员160374 | [南京2024工资与收入](https://tjj.nanjing.gov.cn/bmfw/njsj/202506/t20250624_5592134.html) |
| 十城高校 | 各公报混合口径 | 同一教育部普通高校名单，按所在地聚合 | [教育部名单发布页](https://www.moe.gov.cn/jyb_xxgk/s5743/s5744/A03/202406/t20240621_1136990.html) |

上海年鉴GDP直接发布值精度为0.01万元，保留该精度，没有添加未经证实的小数。其他城市万元转元同理。原三城安居客房价47153/17646/21914已由中指同一2024年12月报告替换；当前来源表全部120条均有值并核对出处。替换了来源与样本，前后变化不能解释为房价涨跌。

## 五城新增公开出处

| 城市 | 经济/公共服务 | 环境/工资补充 |
|---|---|---|
| 杭州 | [杭州市政府新闻办官方账号公报](https://m.thepaper.cn/newsDetail_forward_30453174)、[2025杭州概览附录](https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web149/site/attach/0/2ee3277b2f834c208a1f130966e48bea.pdf) | [2024生态公报](https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3249/site/attach/0/fa8ca80f714b4ed695bb492b94d7b4cb.pdf) |
| 宁波 | [国家统计局宁波调查队2024统计公报](https://zjzd.stats.gov.cn/gjtjjnbdcd/dcfb/art/2025/art_55a7f3728c094536a389fd794bf51c51.html) | 同公报中的中心城区空气数据 |
| 无锡 | [2024统计公报](https://www.wuxi.gov.cn/doc/2025/04/28/4554447.shtml) | [生态公报解读](https://www.wuxi.gov.cn/doc/2025/06/05/4586367.shtml)、[统计局2024工资](https://tj.wuxi.gov.cn/doc/2025/06/30/4603407.shtml) |
| 合肥 | [市统计公报的区政府PDF镜像](https://www.hfyaohai.gov.cn/group1/M00/92/B2/wKgEHmhSjH-AakEtABFDSWCfbvA509.pdf) | [省统计局非私营分市表官方转载](https://tjj.ahsz.gov.cn/sjsz/tjfx/195884431.html)、[市政府新闻办工资发布](https://m.thepaper.cn/newsDetail_forward_31278781) |
| 常州 | [2024统计公报](https://www.changzhou.gov.cn/gi_news/618174366821577) | [统计局2024工资](https://tjj.changzhou.gov.cn/html/tjj/2025/OPOEMFCL_0702/28760.html) |

政府新闻办公室运营的“杭州发布”“合肥发布”账号注明为官方账号原发/转载，不能混淆成统计局域名原文。只记录能够核对的数值，不以搜索不到的官方原文配上其他网站猜测值。

## 同一份普通高校明细

[教育部源XLS](https://www.moe.gov.cn/jyb_xxgk/s5743/s5744/A03/202406/W020240621412769813275.xls)，截至2024-06-20。原文件SHA256：

`cb952bcd2c715792500d8e5e6baf07e06ceabbb512c2fcb6d922cccf0efe6704`

十城381所保存在 `data/reference/ordinary_universities_2024.csv`。原列“学校名称/学校标识码/所在地/办学层次”映射为 `school_name/school_code/city_name/education_level`；所在地去城市名末尾“市”。以学校标识码检查唯一性，按所在地分组计数，普通高校名单与成人名单分开。

| 城市 | 普通高校数 |
|---|---:|
| 上海 | 69 |
| 苏州 | 25 |
| 南京 | 52 |
| 杭州 | 47 |
| 宁波 | 14 |
| 无锡 | 14 |
| 合肥 | 55 |
| 常州 | 11 |
| 广州 | 84 |
| 深圳 | 10 |

这些值是统一年中快照。与本地年末公报差异可能来自统计范围、校区或年度变动；未将该差异解释成地方统计错误。回归测试会检查明细聚合与指标值一致。

## 十城统一住房、城轨与公园来源

住房使用[中指官方2024年12月百城价格报告](https://cihcdnzip.soufunimg.com/backend/reportCreisFile/90924/a55153f1dd68487dbad84a3ab9e02526.pdf)，[官方目录](https://mreport.cih-index.com/cih/detail/90924.html)。二手住宅表3在PDF第7页、住宅租金表5在第9页；方法在第16/17页。数据采集日为12月25日，范围为市辖区有连续挂牌房源的固定样本小区；房价按小区简单平均、租金按固定挂牌建筑面积权重平均。租金保留元/平方米/月，不用假定面积转换整套租金；二者均非成交价格。

官方PDF SHA256：`9718d83701db6e46a1fec1ef46a55e7fb7b729bb90e01df0067df970cb348ca3`。十城提取值、页码、单位与方法保存在`data/reference/housing_2024_12_evidence.json`。

城轨采用[中城协2024年度统计和分析报告](https://infosharingp2-oss.camet.org.cn/resources/manual/2025/07/25/701542926557253.pdf)，表2（PDF第16—19页），定义第12页。2024年底已投运全部城轨制式，换乘站去重，含有轨电车、市域等，因此字段改为`rail_station_count`，不再称为仅地铁站数。

公园采用[住建部统计年鉴](https://www.mohurd.gov.cn/gongkai/fdzdgknr/sjfb/tjxx/jstjnj/index.html)的2024城市建设统计年鉴XLS，表11-2列G。精确下载链接、城市行号及提取值保存在`data/reference/parks_2024_evidence.json`。这是城市建设统计范围，不混入全市城乡或口袋公园口径；上海512、深圳1343与地方宣传口径973、1320不同，采用统一全国表，未判断地方数字错误。

| 城市 | 二手住宅元/平方米 | 租金元/平方米/月 | 城轨车站 | 城市公园 |
|---|---:|---:|---:|---:|
| 上海 | 59939 | 83.1 | 485 | 512 |
| 苏州 | 23396 | 34.8 | 262 | 175 |
| 南京 | 29989 | 39.0 | 228 | 182 |
| 杭州 | 34829 | 51.6 | 256 | 476 |
| 宁波 | 22930 | 32.8 | 121 | 219 |
| 无锡 | 16084 | 26.4 | 89 | 81 |
| 合肥 | 17656 | 26.7 | 171 | 302 |
| 常州 | 13267 | 23.6 | 43 | 47 |
| 广州 | 36888 | 49.5 | 301 | 678 |
| 深圳 | 67762 | 83.4 | 352 | 1343 |

## 工资、医院及新增两城

宁波医院214、杭州417采用[浙江统计年鉴2025表17-22](https://zjjcmspublicnew.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/cms_files/jcms1/web3077/site/flash/tjj/Reports1/2025%E6%B5%99%E6%B1%9F%E7%BB%9F%E8%AE%A1%E5%B9%B4%E9%89%B4/cn/html/17-22%20%E5%90%84%E5%B8%82%E6%96%87%E5%8C%96%E5%92%8C%E5%8D%AB%E7%94%9F%E4%BA%8B%E4%B8%9A%E4%B8%BB%E8%A6%81%E6%8C%87%E6%A0%87%EF%BC%882024%E5%B9%B4%EF%BC%89.html)明确标注的2024年医院数独立列。官方门户已迁移至新OSS的`/cms_files/`路径；原公报宁波225包括妇保院，已替换为年鉴独立医院分类。

杭州工资162774/92054来自[市政府门户的统计局原文](https://www.hangzhou.gov.cn/art/2025/6/26/art_1229063404_4365938.html)，宁波138210/81595来自[统计局工资公报](https://tjj.ningbo.gov.cn/art/2025/6/30/art_1229042825_58922006.html)，均实际下载核对，采用单位就业/从业人员而非在岗职工口径。

无锡医院220来自[卫健委2024年统计公报](https://wjw.wuxi.gov.cn/doc/2025/07/30/4621003.shtml)的官方图片表；常州医院105来自[江苏统计年鉴2025表16-16](https://tj.jiangsu.gov.cn/2025/nj16/nj1616.htm)，同表复核南京315、苏州282、无锡220。不采用无锡综合医院55或常州医院/卫生院/妇幼157合计。

广州经济与医院336采用[2024统计公报](https://tjj.gz.gov.cn/gkmlpt/content/10/10203/mpost_10203416.html)，工资159312/82907采用[统计局工资公报](https://tjj.gz.gov.cn/stats_newtjyw/tjsj/tjgb/qtgb/content/mpost_10330995.html)，空气21μg/m³、94.0%来自[生态公报PDF第4页](https://sthjj.gz.gov.cn/attachment/7/7826/7826916/10298026.pdf)。

深圳经济、医院162和空气来自[2024统计公报](https://tjj.sz.gov.cn/gkmlpt/content/12/12190/mpost_12190509.html)，工资174478/95217来自[统计局工资公报](https://tjj.sz.gov.cn/gkmlpt/content/12/12253/mpost_12253352.html)。PM2.5保留统计公报一位小数17.3；生态公报17为整数发布精度。

## 完整性及边界

发布流程要求每座城市12项原始指标全部有值、来源标记verified并注明复核日期；未来数据若缺失或未核对会直接阻止发布。派生比值不重复计入完整性。

住房12月挂牌样本、全年经济/空气、年末资源存量、年中高校快照都属于2024年度，但不是同一天或相同行政范围。空气仍有市区/中心城区/全市差异，医院/高校/城轨/公园没有人口归一，详见各条notes与模型局限。完整数据不等于完整宜居结论。
