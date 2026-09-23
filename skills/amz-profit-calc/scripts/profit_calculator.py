#!/usr/bin/env python3
"""
profit_calculator.py — Amazon FBA 利润测算 / 隐赚评分 / 盈亏平衡（amz-profit-calc）

输入：成本、售价、重量、各项费率（均有合理默认值）。
输出：成本结构、毛利、净利、盈亏平衡销量、退货敏感性、隐赚(HPI)评分、轻量利润评分。

只做纯计算，不联网；真实价格/费用/月销数据用 cli_call.sh ProductRequest / AsinSalesVolume 拉取后填进来。

用法：
  python3 scripts/profit_calculator.py --price 24.99 --cost 6.5 --weight 0.35
  python3 scripts/profit_calculator.py --price 24.99 --cost 6.5 --weight 0.35 --monthly-sales 800 --referral-rate 0.15 --ad-rate 0.15
  python3 scripts/profit_calculator.py --json   # 演示内置样例
"""
import argparse
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def estimate_fba_fee(weight_kg: float) -> float:
    """按重量粗估 FBA 配送费（USD）。正式请以 ProductRequest.FbaFee 或官方 Revenue Calculator 为准。"""
    # 与 seller-agent calculator.py 一致的粗估：max(3.5, kg*2.5+1.5)
    return max(3.5, weight_kg * 2.5 + 1.5)


def compute(price, cost, weight_kg, referral_rate=0.15, ad_rate=0.15,
            fixed_monthly=500.0, return_rate=0.05, monthly_sales=None,
            fba_fee_override=None):
    """返回利润测算 dict（金额单位 USD）。"""
    fba_fee = fba_fee_override if fba_fee_override is not None else estimate_fba_fee(weight_kg)
    referral_fee = price * referral_rate
    ad_cost = price * ad_rate

    # 单均成本
    variable_cost = cost + fba_fee + referral_fee + ad_cost
    gross_profit = price - variable_cost           # 未扣退货的单均利润
    margin = (gross_profit / price * 100) if price else 0.0

    # 退货侵蚀：每退一单损失 = 该单利润 + 退件处理费(~3.5)
    loss_per_return = gross_profit + 3.5
    eff_gross_profit = gross_profit - loss_per_return * return_rate
    eff_margin = (eff_gross_profit / price * 100) if price else 0.0

    # 盈亏平衡（按月固定成本 fixed_monthly）
    if eff_gross_profit > 0:
        be_monthly = fixed_monthly / eff_gross_profit
        be_daily = be_monthly / 30
        breakeven = f"~{be_daily:.1f} 单/天（按月固定成本 ${fixed_monthly:.0f}）"
    else:
        be_monthly = be_daily = None
        breakeven = "无法盈亏平衡（单均为负）"

    # 隐赚指数(HPI 代理分, 0-100)：综合毛利、竞争友好度(FBA费/价格)、轻量度
    # 注意：这是本地代理分，Sorftime 官方 HPI 请用 MCP potential_product
    hpi = _hpi_proxy(margin, fba_fee, price, weight_kg)

    # 轻量利润效率 = (毛利率 × 月销) / FBA费
    if monthly_sales and fba_fee > 0:
        profit_eff = (margin / 100 * price * monthly_sales) / fba_fee
    else:
        profit_eff = None

    # 月净利（若给了月销）
    net_monthly = eff_gross_profit * monthly_sales - fixed_monthly if monthly_sales else None

    return {
        "售价": f"${price:.2f}",
        "采购成本": f"${cost:.2f}",
        "FBA配送费(估)": f"${fba_fee:.2f}",
        "平台佣金({:.0%})".format(referral_rate): f"${referral_fee:.2f}",
        "广告成本({:.0%})".format(ad_rate): f"${ad_cost:.2f}",
        "单均总成本": f"${variable_cost:.2f}",
        "单均毛利(未扣退货)": f"${gross_profit:.2f}",
        "毛利率": f"{margin:.1f}%",
        f"退货率{return_rate:.0%}后单均净利": f"${eff_gross_profit:.2f}（{eff_margin:.1f}%）",
        "盈亏平衡": breakeven,
        "隐赚指数(代理分)": f"{hpi}/100",
        "轻量利润效率": (f"{profit_eff:.0f}" if profit_eff is not None else "需传 --monthly-sales"),
        "月净利": (f"${net_monthly:.0f}" if net_monthly is not None else "需传 --monthly-sales"),
        "建议": _suggest(margin, eff_margin, weight_kg),
    }


def _hpi_proxy(margin, fba_fee, price, weight_kg):
    """本地 HPI 代理分：毛利高 + FBA费占比低 + 轻量 = 分高。仅作排序参考。"""
    score = 0.0
    # 毛利 40 分
    score += min(margin, 60) / 60 * 40
    # FBA 费占比低 30 分（占售价比 <10% 满分）
    fba_ratio = fba_fee / price if price else 1
    score += max(0.0, (0.18 - fba_ratio) / 0.18) * 30
    # 轻量 30 分（<0.5kg 满分）
    score += max(0.0, (0.8 - weight_kg) / 0.8) * 30
    return round(score, 1)


def _suggest(margin, eff_margin, weight_kg):
    bits = []
    if eff_margin >= 30:
        bits.append("净利健康，值得推进")
    elif eff_margin >= 18:
        bits.append("净利中等，控广告与退货")
    elif eff_margin >= 10:
        bits.append("净利薄，优化成本或提价")
    else:
        bits.append("净利过低，不建议")
    if weight_kg > 1.0:
        bits.append("⚠️ 偏重，FBA 费阶可能偏高，用官方 Revenue Calculator 复核")
    return " | ".join(bits)


def main():
    p = argparse.ArgumentParser(description="Amazon FBA 利润测算")
    p.add_argument("--price", type=float, help="售价 USD")
    p.add_argument("--cost", type=float, help="采购成本 USD（含头程到 FBA）")
    p.add_argument("--weight", type=float, default=0.5, help="单件重量 kg")
    p.add_argument("--referral-rate", type=float, default=0.15, help="平台佣金率, 默认 0.15")
    p.add_argument("--ad-rate", type=float, default=0.15, help="广告占售价比, 默认 0.15")
    p.add_argument("--fixed-monthly", type=float, default=500.0, help="月固定成本 USD")
    p.add_argument("--return-rate", type=float, default=0.05, help="退货率, 默认 0.05")
    p.add_argument("--monthly-sales", type=int, default=None, help="预估月销量")
    p.add_argument("--fba-fee", type=float, default=None, help="用 ProductRequest 拉到的真实 FBA 费覆盖估算")
    p.add_argument("--json", action="store_true", help="输出 JSON（含内置演示样例）")
    args = p.parse_args()

    if args.json or args.price is None or args.cost is None:
        demo = compute(price=24.99, cost=6.5, weight_kg=0.35, monthly_sales=800)
        print(json.dumps({"demo": demo}, ensure_ascii=False, indent=2))
        if args.price is None:
            return

    res = compute(
        price=args.price, cost=args.cost, weight_kg=args.weight,
        referral_rate=args.referral_rate, ad_rate=args.ad_rate,
        fixed_monthly=args.fixed_monthly, return_rate=args.return_rate,
        monthly_sales=args.monthly_sales, fba_fee_override=args.fba_fee,
    )
    print("# Amazon FBA 利润测算")
    print()
    for k, v in res.items():
        print(f"- **{k}**: {v}")


if __name__ == "__main__":
    main()
