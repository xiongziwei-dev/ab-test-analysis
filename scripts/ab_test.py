import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt

# 设置随机种子，确保每次运行结果一致
np.random.seed(42)

# 1. 模拟 A/B 实验数据

n = 10000  # 总用户数

# 用户ID：1 到 10000
user_id = np.arange(1, n + 1)

# 随机分配组别：control（对照组） vs treatment（实验组），各50%
group = np.random.choice(['control', 'treatment'], size=n, p=[0.5, 0.5])

# 模拟转化行为：对照组转化率 10%，实验组提升至 12%
conversion_rate = {'control': 0.10, 'treatment': 0.12}
converted = np.array([
    np.random.binomial(1, conversion_rate[g]) for g in group
])

# 模拟消费金额（只有转化的用户才有消费）
# 假设客单价服从正态分布，均值120，标准差20，最低50元，最高300元
revenue = np.where(
    converted == 1,
    np.random.normal(120, 20, n).clip(50, 300),
    0
)

# 构建 DataFrame
df = pd.DataFrame({
    'user_id': user_id,
    'group': group,
    'converted': converted,
    'revenue': revenue
})

print("前5行数据预览：")
print(df.head())
print(f"\n对照组样本数: {len(df[df['group']=='control'])}")
print(f"实验组样本数: {len(df[df['group']=='treatment'])}")

# ====================================================
# 2. 转化率分析：双样本 Z 检验
# ====================================================
control = df[df['group'] == 'control']
treatment = df[df['group'] == 'treatment']

conversions = [control['converted'].sum(), treatment['converted'].sum()]
nobs = [len(control), len(treatment)]

z_stat, p_value = proportions_ztest(conversions, nobs, alternative='two-sided')

print("\n========== 转化率分析 ==========")
print(f"对照组转化率: {control['converted'].mean():.4f}")
print(f"实验组转化率: {treatment['converted'].mean():.4f}")
print(f"Z 统计量: {z_stat:.4f}")
print(f"p 值: {p_value:.4f}")
if p_value < 0.05:
    print("结论：p < 0.05，实验组转化率显著提升，建议上线优惠券策略。")
else:
    print("结论：p >= 0.05，无显著差异，策略效果不明显。")

# ====================================================
# 3. 客单价分析：独立样本 T 检验（仅含转化用户）
# ====================================================
control_rev = control[control['converted'] == 1]['revenue']
treatment_rev = treatment[treatment['converted'] == 1]['revenue']

t_stat, p_val_rev = stats.ttest_ind(control_rev, treatment_rev, equal_var=False)

print("\n========== 客单价分析 ==========")
print(f"对照组客单价均值: {control_rev.mean():.2f}")
print(f"实验组客单价均值: {treatment_rev.mean():.2f}")
print(f"T 统计量: {t_stat:.4f}")
print(f"p 值: {p_val_rev:.4f}")
if p_val_rev < 0.05:
    print("结论：p < 0.05，实验组客单价有显著变化。")
else:
    print("结论：p >= 0.05，客单价无显著差异，优惠券可能未影响消费金额。")

# ====================================================
# 4. 可视化：转化率对比 + 客单价分布
# ====================================================
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# 4.1 转化率柱状图（带误差线）
groups = ['Control', 'Treatment']
rates = [control['converted'].mean(), treatment['converted'].mean()]
se = [np.sqrt(r * (1 - r) / n) for r, n in zip(rates, nobs)]
bars = ax[0].bar(groups, rates, yerr=se, capsize=10, color=['gray', 'steelblue'])
ax[0].set_ylabel('Conversion Rate')
ax[0].set_title('Conversion Rate Comparison with Error Bars')
for bar, rate in zip(bars, rates):
    ax[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
               f'{rate:.2%}', ha='center', fontsize=11)

# 4.2 客单价箱线图
rev_data = [control_rev, treatment_rev]
bp = ax[1].boxplot(rev_data, labels=['Control', 'Treatment'], patch_artist=True)
bp['boxes'][0].set_facecolor('lightgray')
bp['boxes'][1].set_facecolor('lightsteelblue')
ax[1].set_ylabel('Revenue per Order')
ax[1].set_title('Revenue Distribution Comparison')

plt.tight_layout()
plt.savefig('ab_test_results.png', dpi=150)
plt.show()
print("\n图表已保存为 ab_test_results.png")