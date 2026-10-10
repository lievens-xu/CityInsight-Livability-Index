# 2024 数据来源与口径审计

复核日期：2026-10-10。数据所属年度为2024，不因2025或2026年的网页发布时间而改变。完整字段、数值、精确URL和复核状态保存在 `data/raw/data_source_tracking_2024.csv`，看板可直接查询。

## 原三城更正

| 项目 | 原值/做法 | 当前值/做法 | 依据 |
|---|---|---|---|
| 上海人均GDP | 217424，按年末人口估算 | 217100，直接发布21.71万元转元 | [上海统计年鉴2025 表1.5](https://tjj.sh.gov.cn/tjnj/2025tjnj/C01/C0105B.htm) |
| 南京人均GDP | 193180，按年末人口估算 | 193483，直接发布值 | [南京2024统计公报](https://tjj.nanjing.gov.cn/njstjj/202504/t20250401_5108470.html) |
| 苏州非私营工资 | 在岗职工143611 | 从业人员141827 | [苏州统计局问答](https://tjj.suzhou.gov.cn/sztjj/rdwd/202506/1e244bbcb19c4036922eb1c25f4991e1.shtml) |
| 南京非私营工资 | 在岗职工165726 | 从业人员160374 | [南京2024工资与收入](https://tjj.nanjing.gov.cn/bmfw/njsj/202506/t20250624_5592134.html) |
| 八城高校 | 各公报混合口径 | 同一教育部普通高校名单，按所在地聚合 | [教育部名单发布页](https://www.moe.gov.cn/jyb_xxgk/s5743/s5744/A03/202406/t20240621_1136990.html) |

上海年鉴GDP直接发布值精度为0.01万元，保留该精度，没有添加未经证实的小数。其他城市万元转元同理。原三城房价47153/17646/21914仍保留，均标为`pending`，本次历史网页未能读取；这部分仅用于暂定模型演示，不能宣称已完成事实核验。

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

八城287所保存在 `data/reference/ordinary_universities_2024.csv`。原列“学校名称/学校标识码/所在地/办学层次”映射为 `school_name/school_code/city_name/education_level`；所在地去城市名末尾“市”。以学校标识码检查唯一性，按所在地分组计数，普通高校名单与成人名单分开。

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

这些值是统一年中快照。与本地年末公报差异可能来自统计范围、校区或年度变动；未将该差异解释成地方统计错误。回归测试会检查明细聚合与指标值一致。

## 没有填入的近似数据

- 无锡“综合医院55”只是医院子类；常州“医院、卫生院含妇幼157”为合计；宁波“医院含妇保225”的分类不同，因此医院总数留空。
- 杭州、宁波2024工资原文访问未成功，未用普通转载填入；原文链接保留在研究记录中，不标成verified。
- 市区/中心城区空气监测与全行政区不是同一覆盖范围，notes中明确标记。
- 公园“当年新增”不能充作年末存量；高校“含成人”不能充作普通高校数量。
- 没有虚构住房、租金、地铁或公园数据来制造完整排名。
