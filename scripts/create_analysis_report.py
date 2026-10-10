"""Generate the current report from data, avoiding stale hand-written rankings."""
import json
from model import BASE_DIR, RAW_INDICATORS, read_csv_safely


def main():
    scores = read_csv_safely(BASE_DIR / 'data/processed/livability_scores_2024.csv')
    scenarios = read_csv_safely(BASE_DIR / 'data/processed/preference_scenarios_2024.csv')
    source = read_csv_safely(BASE_DIR / 'data/raw/data_source_tracking_2024.csv')
    sensitivity = json.loads((BASE_DIR / 'data/processed/weight_sensitivity_2024.json').read_text())['cities']
    lines = ['# CityInsight 2024 数据与偏好分析报告', '',
             '> 本报告由 `scripts/create_analysis_report.py` 从实际输出生成。2024是数据年度，2026-10-10是来源复核日期。', '',
             '## 数据覆盖', '', '| 城市 | 有值原始指标 | 覆盖率 | 当前状态 |', '|---|---:|---:|---|']
    for row in scores.sort_values('city_id').itertuples():
        lines.append(f'| {row.city_name} | {row.available_indicators}/{len(RAW_INDICATORS)} | {row.coverage * 100:.1f}% | {"暂定排名" if row.status == "provisional" else "数据不足，保留原值不排名"} |')
    verified = int(((source.verification_status == 'verified') & source.value.notna()).sum())
    pending = int(((source.verification_status != 'verified') & source.value.notna()).sum())
    lines += ['', f'共{int(source.value.notna().sum())}条有值原始指标，其中{verified}条核对了公开来源，{pending}条为未复核的历史记录。派生房价收入比不计入原始指标覆盖率。', '',
              '## 默认权重下的暂定结果', '', '| 城市 | 经济机会 | 生活成本 | 公共服务 | 环境质量 | 总分 | 排名 |', '|---|---:|---:|---:|---:|---:|---:|']
    for row in scores[scores.status == 'provisional'].itertuples():
        lines.append(f'| {row.city_name} | {row.economy_score:.1f} | {row.cost_score:.1f} | {row.service_score:.1f} | {row.environment_score:.1f} | {row.total_score:.1f} | {int(row.rank)} |')
    lines += ['', '这些分数仅比较四维数据达到门槛的同年城市。其余城市不共享完整生活成本指标，不应依据经济或空气数据强行给出综合名次。', '',
              '![暂定排名](../dashboard/figures/01_total_score_ranking.png)', '',
              '## 同一数据，不同偏好', '', '| 场景 | 权重（经济/成本/服务/环境） | 暂定排名（总分） |', '|---|---|---|']
    presets = {'balanced': ('默认', '35/30/20/15'), 'career': ('职业发展', '55/20/15/10'), 'budget': ('成本优先', '20/55/15/10'), 'green': ('环境优先', '20/20/20/40')}
    for scenario, (label, weights) in presets.items():
        rows = scenarios[scenarios.scenario == scenario].sort_values(['rank', 'city_id'])
        order = '、'.join(f'{row.city_name} {row.total_score:.1f}' for row in rows.itertuples())
        lines.append(f'| {label} | {weights}% | {order} |')
    lines += ['', '这说明“最适合”取决于维度偏好。比较组及原始数据保持固定，只改变权重；当前生活成本还缺少租金，不能解释成总体生活支出比较。', '',
              '## 权重敏感性', '', '| 城市 | 最好排名 | 最差排名 | 第一名权重组合数（含并列） | 枚举总数 |', '|---|---:|---:|---:|---:|']
    for row in sensitivity:
        lines.append(f'| {row["city_name"]} | {row["best_rank"]} | {row["worst_rank"]} | {row["top_rank_weight_combinations"]} | {row["weight_combinations"]} |')
    lines += ['', '枚举每10个百分点一档、合计100%的四维权重，包含某维权重为0的端点。第一名组合数只是该离散网格下的探索结果，不代表城市宜居概率，也不是抽样统计的置信区间。', '',
              '## 八城经济与空气原始值', '',
              '![GDP与PM2.5](../dashboard/figures/04_gdp_vs_pm25.png)', '',
              '横轴为人均GDP（千元/人），右侧表示人均经济产出更高；纵轴为年均PM2.5（μg/m³），下方表示颗粒物浓度更低。每个点是一座城市，图中使用原始值，不使用综合得分。经济产出不能替代个人工资或就业机会，监测范围也存在市区与全市差异。', '',
              '## 已修正与统一的口径', '',
              '- 上海人均GDP采用官方直接公布21.71万元换算元，替换原年末人口估算217424元；保留原发布精度。',
              '- 南京人均GDP采用统计公报直接值193483元，替换年末人口估算193180元。',
              '- 苏州非私营年工资统一为从业人员141827元（原143611是“在岗职工”）；南京统一为从业人员160374元（原165726是“在岗职工”）。派生房价收入比已重算。',
              '- 八城普通高校均来自教育部截至2024-06-20同一份名单的所在地聚合，保存287所明细，避免跨城市混合普通高校、全部高校和年末公报口径。',
              '- 无锡仅综合医院55、常州医院与卫生院合计157、宁波医院含妇保院225均不直接填入统一医院字段。', '',
              '## 当前缺口与结论边界', '',
              '- 五城缺少统一时点的住房指标；现有三城房价历史值尚未复核。租金、地铁站和公园存量全城待补。',
              '- 杭州与宁波年工资还未读到可核实的官方正文，未使用转载数字补齐。',
              '- 医院与高校未人口归一，住房指标存在重复影响；小样本Min-Max会放大差异。',
              '- 当前结果支持流程验证与偏好探索，不支持完整八城宜居性结论。数据补齐会改变比较组与分数。', '',
              '来源和复核方法见 [数据来源审计](data_source_audit_2024.md)，模型定义见 [指标体系](indicator_system.md)。', '']
    output = BASE_DIR / 'docs/analysis_report_2024_mvp.md'
    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Generated: {output}')


if __name__ == '__main__':
    main()
