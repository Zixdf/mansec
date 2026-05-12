import os
import random
from html2image import Html2Image
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 认准这个路径：保存在 phishing 文件夹里
OUTPUT_DIR = os.path.join(BASE_DIR, 'dataset', 'train', 'phishing')
os.makedirs(OUTPUT_DIR, exist_ok=True)

hti = Html2Image(size=(800, 800), output_path=OUTPUT_DIR)

# ==================== 模板 1：红色警告风 (WebMail 爆满) ====================
html_style_1 = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: 'Segoe UI', sans-serif; background-color: #f3f2f1; display: flex; flex-direction: column; height: 768px; overflow: hidden; }}
  .content-area {{ flex: 1; background-color: white; margin: 15px; border: 2px solid #e81123; }}
  .mail-title {{ font-size: 24px; font-weight: bold; color: #e81123; margin: 20px 30px; }}
  .warning-banner {{ background-color: #e81123; color: white; padding: 15px; font-weight: bold; text-align: center; }}
  .quota-box {{ border: 3px dashed #e81123; padding: 20px; background: #fff0f0; width: 60%; margin: 20px auto; text-align: center; font-size: 20px; color: #d13438; }}
  .cta-btn {{ background-color: #e81123; color: white; border: none; padding: 18px 40px; font-size: 20px; font-weight: bold; cursor: pointer; display: block; margin: 30px auto; }}
</style></head><body>
  <div class="content-area">
    <h1 class="mail-title">⚠ 最终通知：账户即将锁定</h1>
    <div class="warning-banner">系统拦截警告：请立即采取行动！</div>
    <div class="quota-box">存储容量: {var1} GB / {var2} GB<br><span style="font-size: 14px;">(状态：已爆满)</span></div>
    <p style="text-align: center;">您必须在24小时内验证身份。</p>
    <button class="cta-btn">{btn_text}</button>
  </div>
</body></html>
"""

# ==================== 模板 2：冷淡官方风 (伪造 PayPal/银行 异常账单) ====================
html_style_2 = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: Arial, sans-serif; background-color: #f4f6f8; display: flex; justify-content: center; align-items: center; height: 768px; }}
  .card {{ background: white; width: 600px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden; border-top: 6px solid #003087; }}
  .header {{ padding: 30px; text-align: center; border-bottom: 1px solid #eee; }}
  .logo {{ font-size: 28px; font-weight: bold; color: #003087; font-style: italic; }}
  .content {{ padding: 40px; color: #333; }}
  .amount {{ font-size: 36px; font-weight: bold; color: #111; text-align: center; margin: 20px 0; }}
  .cta-btn {{ background-color: #0070ba; color: white; border: none; padding: 15px; font-size: 18px; border-radius: 25px; cursor: pointer; display: block; width: 100%; text-align: center; text-decoration: none; font-weight: bold; margin-top: 30px; }}
</style></head><body>
  <div class="card">
    <div class="header"><div class="logo">PaySecured 支付凭证</div></div>
    <div class="content">
      <p>尊敬的用户，您好：</p>
      <p>我们注意到您的账户刚刚向 <strong>{var1}</strong> 支付了一笔款项。如果这不是您本人的操作，请立即取消此交易。</p>
      <div class="amount">交易金额: $ {var2}</div>
      <button class="cta-btn">{btn_text}</button>
      <p style="font-size: 12px; color: #888; text-align: center; margin-top: 30px;">如果您不认识此交易，点击上方按钮进入安全中心拦截。</p>
    </div>
  </div>
</body></html>
"""

# ==================== 模板 3：企业办公风 (伪造 SharePoint/发票共享) ====================
html_style_3 = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: 'Segoe UI', sans-serif; background-color: white; height: 768px; }}
  .top-bar {{ background: #0078d4; height: 50px; display: flex; align-items: center; padding-left: 20px; color: white; font-weight: bold; font-size: 18px; }}
  .container {{ padding: 50px; }}
  .doc-card {{ border: 1px solid #c8c6c4; padding: 30px; display: flex; align-items: center; background: #f3f2f1; max-width: 500px; margin-top: 20px; border-radius: 4px; }}
  .icon {{ font-size: 40px; margin-right: 20px; }}
  .cta-btn {{ background-color: white; color: #0078d4; border: 1px solid #0078d4; padding: 10px 20px; cursor: pointer; font-weight: bold; margin-top: 10px; }}
</style></head><body>
  <div class="top-bar">Office 协作平台</div>
  <div class="container">
    <h2 style="color: #323130; font-weight: normal;"><strong>{var1}</strong> 与您共享了一个加密的文档。</h2>
    <p style="color: #605e5c;">此消息由系统自动生成，该文档包含敏感的财务数据，需要您登录域账户以验证查看权限。</p>
    <div class="doc-card">
      <div class="icon">📊</div>
      <div>
        <div style="font-weight: bold; font-size: 18px; margin-bottom: 5px;">{var2}</div>
        <div style="color: #605e5c; font-size: 14px;">1.4 MB - 仅限受邀者访问</div>
        <button class="cta-btn">{btn_text}</button>
      </div>
    </div>
  </div>
</body></html>
"""

print("🚀 正在生成 100 张【多风格】的钓鱼邮件截图...")

# 👇 核心：先数一数 phishing 文件夹里已经有几张钓鱼图片了
exist_count = len(os.listdir(OUTPUT_DIR))

for i in range(300):
    # 随机选择一种风格
    style_choice = random.choice([i])

    if style_choice == 1:
        q_total = random.choice([i])
        q_used = round(q_total + random.uniform(0.5, 2.5), 1)
        btn = random.choice(["立即验证您的账户", "清除存储并恢复", "升级配额 (紧急)"])
        html_str = html_style_1.format(var1=q_used, var2=q_total, btn_text=btn)

    elif style_choice == 2:
        merchant = random.choice(["Apple Store", "Crypto Exchange Inc.", "Steam Games", "海外商户"])
        amount = round(random.uniform(199.99, 2999.99), 2)
        btn = random.choice(["这不是我操作的 - 立即取消", "拦截并退款", "报告账户被盗"])
        html_str = html_style_2.format(var1=merchant, var2=amount, btn_text=btn)

    else:
        hr_name = random.choice(["HR Department", "财务部-李明", "CEO Office", "IT Support"])
        doc_name = random.choice(["2026年薪酬调整明细.xlsx", "Q3裁员名单_绝密.pdf", "员工福利升级确认单.docx"])
        btn = random.choice(["使用域账号登录查看", "在线预览文档", "安全下载"])
        html_str = html_style_3.format(var1=hr_name, var2=doc_name, btn_text=btn)

    # 👇 自动顺延命名：接着之前的数字往下排！认准 phishing_ 前缀！
    filename = f"phishing_{exist_count + i + 1:03d}.png"

    try:
        hti.screenshot(html_str=html_str, save_as=filename)
    except Exception as e:
        print(f"⚠️ 第 {exist_count + i + 1} 张截图生成失败: {e}")
        pass

    if (i + 1) % 10 == 0:
        print(f"✅ 本次已完成: {i + 1} 张 (钓鱼图库总数: {exist_count + i + 1})")

print("🎉 混合风格钓鱼邮件生成完毕！快去喂给模型吧！")