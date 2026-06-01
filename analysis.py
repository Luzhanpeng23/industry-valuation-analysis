import pandas as pd
import matplotlib.pyplot as plt


# 读取数据，按行业分组聚合
def load_data():
    df = pd.read_csv('industry_data.csv')
    # 按行业算平均PE、平均PB、总市值
    stats = df.groupby('行业').agg({'PE': 'mean', 'PB': 'mean', '市值': 'sum'}).reset_index()
    stats.columns = ['行业', '平均PE', '平均PB', '总市值']
    return stats


# 判断估值洼地：PE和PB都低于中位数
def find_pit(stats):
    pe_mid = stats['平均PE'].median()
    pb_mid = stats['平均PB'].median()
    stats['洼地'] = (stats['平均PE'] < pe_mid) & (stats['平均PB'] < pb_mid)
    return stats, pe_mid, pb_mid


# 画气泡图
def draw_bubble(stats, pe_mid, pb_mid):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(10, 7))

    # 气泡大小按市值缩放
    max_val = stats['总市值'].max()
    sizes = [v / max_val * 2000 for v in stats['总市值']]

    # 洼地标红
    color_list = []
    for flag in stats['洼地']:
        if flag:
            color_list.append('red')
        else:
            color_list.append('steelblue')

    # 逐个画气泡
    for i in range(len(stats)):
        row = stats.iloc[i]
        ax.scatter(row['平均PE'], row['平均PB'], s=sizes[i],
                   c=color_list[i], alpha=0.6, edgecolors='white', linewidth=2)
        label = f'{row["行业"]}\n{row["总市值"]/10000:.1f}万亿'
        ax.annotate(label, (row['平均PE'], row['平均PB']),
                    ha='center', va='center', fontsize=10)

    # 画中位数参考线
    ax.axhline(y=pb_mid, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=pe_mid, color='gray', linestyle='--', alpha=0.5)

    ax.set_xlabel('平均PE')
    ax.set_ylabel('平均PB')
    ax.set_title('行业估值气泡图（气泡大小=行业市值）')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('industry_valuation_bubble.png', dpi=150)
    plt.show()


def main():
    stats = load_data()
    print("各行业估值统计：")
    print(stats)
    print()

    stats, pe_mid, pb_mid = find_pit(stats)
    print(f'PE中位数: {pe_mid:.2f}')
    print(f'PB中位数: {pb_mid:.2f}')

    # 输出估值洼地行业
    pit = stats[stats['洼地']]['行业'].tolist()
    if pit:
        print(f'估值洼地行业: {", ".join(pit)}')
        print('说明: 这些行业PE和PB都低于中位数，可能被低估')
    else:
        print('没有发现估值洼地')

    # 画图
    draw_bubble(stats, pe_mid, pb_mid)


if __name__ == '__main__':
    main()
