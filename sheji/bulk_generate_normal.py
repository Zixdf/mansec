import os
import random
from html2image import Html2Image
from datetime import datetime, timedelta

# 1. 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 认准这个路径：保存在 normal 文件夹里
OUTPUT_DIR = os.path.join(BASE_DIR, 'dataset', 'train', 'normal')
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    hti = Html2Image(size=(800, 800), output_path=OUTPUT_DIR)
except Exception as e:
    print(f"❌ 初始化截图工具失败: {e}")
    exit()

# ==========================================
# HTML 模板定义区
# ==========================================

style_1_html = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: 'Segoe UI', sans-serif; background-color: #f3f2f1; display: flex; flex-direction: column; height: 800px; overflow: hidden; }}
  .navbar {{ background-color: #0078d4; height: 48px; display: flex; align-items: center; padding: 0 20px; color: white; }}
  .main {{ display: flex; flex: 1; }}
  .sidebar {{ width: 200px; background-color: white; border-right: 1px solid #e1dfdd; padding: 20px 0; }}
  .menu-item {{ padding: 12px 20px; font-size: 14px; color: #333; }}
  .menu-item.active {{ background-color: #f3f2f1; font-weight: 600; border-left: 3px solid #0078d4; }}
  .content-area {{ flex: 1; background-color: white; margin: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 30px; }}
  .avatar {{ width: 40px; height: 40px; background-color: {avatar_color}; border-radius: 50%; color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; float: left;}}
  .mail-title {{ font-size: 22px; font-weight: 600; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
  .sender-name {{ font-weight: 600; font-size: 14px; margin: 0; }}
  .mail-date {{ font-size: 12px; color: #605e5c; }}
  .mail-body {{ padding-top: 20px; font-size: 15px; color: #333; line-height: 1.6; clear: both;}}
</style></head><body>
  <div class="navbar">::: 企业邮件系统</div>
  <div class="main">
    <div class="sidebar"><div class="menu-item active">收件箱</div><div class="menu-item">已发送</div></div>
    <div class="content-area">
      <h1 class="mail-title">{subject}</h1>
      <div class="avatar">{avatar_text}</div>
      <div><p class="sender-name">{sender}</p><p class="mail-date">{date}</p></div>
      <div class="mail-body">{content}<br><br>祝好，<br>团队敬上</div>
    </div>
  </div>
</body></html>
"""

style_2_html = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: Arial, sans-serif; background-color: #ffffff; padding: 40px; height: 800px; box-sizing: border-box; }}
  .search-pill {{ background: #f1f3f4; border-radius: 24px; padding: 12px 20px; color: #5f6368; font-size: 14px; margin-bottom: 40px; }}
  .mail-title {{ font-size: 24px; color: #202124; margin-bottom: 25px; font-weight: normal; }}
  .header-row {{ display: flex; align-items: center; margin-bottom: 30px; }}
  .avatar {{ width: 40px; height: 40px; background-color: {avatar_color}; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 18px; margin-right: 15px; }}
  .sender-info {{ flex: 1; }}
  .sender-name {{ font-weight: bold; color: #202124; font-size: 14px; margin: 0; }}
  .mail-date {{ color: #5f6368; font-size: 12px; margin: 0; text-align: right; }}
  .mail-body {{ font-size: 14px; color: #202124; line-height: 1.8; }}
</style></head><body>
  <div class="search-pill">🔍 在邮件中搜索</div>
  <h1 class="mail-title">{subject}</h1>
  <div class="header-row">
    <div class="avatar">{avatar_text}</div>
    <div class="sender-info"><p class="sender-name">{sender}</p><p style="margin:0; font-size:12px; color:#5f6368;">发给 我</p></div>
    <div class="mail-date">{date}</div>
  </div>
  <div class="mail-body">{content}</div>
</body></html>
"""

style_3_html = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: Helvetica, sans-serif; background-color: #f4f5f7; display: flex; justify-content: center; padding-top: 40px; height: 800px; }}
  .card {{ background: white; width: 600px; border-radius: 8px; box-shadow: 0 3px 6px rgba(0,0,0,0.05); overflow: hidden; }}
  .card-header {{ background: #172b4d; padding: 20px; color: white; font-weight: bold; display: flex; align-items: center; }}
  .card-body {{ padding: 30px; }}
  .action-title {{ font-size: 18px; color: #172b4d; margin-top: 0; }}
  .task-box {{ border-left: 4px solid #0052cc; background: #fafbfc; padding: 15px; margin: 20px 0; color: #172b4d; font-weight: 500; }}
  .btn {{ background: #0052cc; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: bold; margin-top: 10px; }}
  .footer {{ text-align: center; color: #6b778c; font-size: 12px; padding: 20px; border-top: 1px solid #dfe1e6; }}
</style></head><body>
  <div class="card">
    <div class="card-header">☑️ 任务管理中心</div>
    <div class="card-body">
      <h2 class="action-title">{sender} 给您分配了一个新任务</h2>
      <div class="task-box">[{avatar_text}-1024] {subject}</div>
      <p style="color: #42526e; line-height: 1.6;">{content}</p>
      <div class="btn">查看任务详情</div>
    </div>
    <div class="footer">系统自动发送，请勿回复。<br>{date}</div>
  </div>
</body></html>
"""

style_4_html = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: 'Courier New', Courier, monospace; background-color: #ffffff; height: 800px; }}
  .header {{ background: #24292e; color: white; padding: 15px 30px; font-size: 16px; font-family: sans-serif; }}
  .success-banner {{ background: #e6ffed; border: 1px solid #b7eb8f; color: #2ebc4f; padding: 15px 30px; font-weight: bold; font-family: sans-serif; display: flex; align-items: center; }}
  .log-box {{ background: #f6f8fa; padding: 20px; margin: 30px; border-radius: 6px; font-size: 13px; color: #24292e; border: 1px solid #e1e4e8; }}
  .meta {{ color: #586069; padding: 0 30px; font-family: sans-serif; font-size: 12px; }}
</style></head><body>
  <div class="header">⚙️ CI/CD Pipeline Notification</div>
  <div class="success-banner">✅ {subject}</div>
  <div class="log-box">
    <strong>[DEPLOYMENT SUCCESS]</strong><br><br>
    Initiated by: {sender}<br>
    Timestamp: {date}<br><br>
    Details:<br>
    {content}
  </div>
  <div class="meta">If you did not initiate this deployment, please check the system logs.</div>
</body></html>
"""

style_5_html = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  body {{ margin: 0; font-family: 'Microsoft YaHei', sans-serif; background-color: #f9f9f9; padding: 30px; height: 800px; }}
  .paper {{ background: white; border-top: 5px solid #d4af37; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: relative; }}
  .stamp {{ position: absolute; top: 30px; right: 40px; color: #2ebc4f; border: 2px solid #2ebc4f; padding: 5px 15px; font-weight: bold; font-size: 18px; transform: rotate(15deg); border-radius: 4px; }}
  .title {{ font-size: 20px; font-weight: bold; margin-bottom: 30px; color: #333; text-align: center; }}
  .table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
  .table th, .table td {{ border: 1px solid #e1e1e1; padding: 12px; font-size: 14px; }}
  .table th {{ background: #f5f5f5; width: 120px; text-align: left; color: #666; }}
  .footer {{ font-size: 12px; color: #999; text-align: center; margin-top: 40px; }}
</style></head><body>
  <div class="paper">
    <div class="stamp">审批通过</div>
    <div class="title">OA 流程审批结果通知</div>
    <table class="table">
      <tr><th>流程主题</th><td>{subject}</td></tr>
      <tr><th>发起人</th><td>{sender}</td></tr>
      <tr><th>完成时间</th><td>{date}</td></tr>
      <tr><th>审批意见</th><td>同意。{content}</td></tr>
    </table>
    <p style="font-size: 14px; line-height: 1.6; color: #333;">该流程已流转完毕并归档，您可以登录系统查看详细进度。</p>
    <div class="footer">OA 办公自动化系统自动发送</div>
  </div>
</body></html>
"""

# ==========================================
# 语料库
# ==========================================

data_1_pool = [
    {"sender": "HR Team <hr@company.com>", "avatar": "HR", "color": "#107c41", "subject": "本周工作周报汇总",
     "content": "附件是本周各部门的工作周报汇总，请查阅。如有遗漏请在下班前补充。"},
    {"sender": "Admin <admin@company.com>", "avatar": "AD", "color": "#0078d4", "subject": "关于端午节放假安排的通知",
     "content": "根据国家法定节假日安排，现将端午节放假时间通知如下，请大家提前做好工作安排。"},
    {"sender": "IT Support <it@company.com>", "avatar": "IT", "color": "#8e24aa", "subject": "周五凌晨机房网络升级通知",
     "content": "为提升内网访问速度，IT部将于本周五凌晨 2:00-4:00 进行核心交换机割接，期间办公网将短暂中断。"},
    {"sender": "Finance Dept <fin@company.com>", "avatar": "FI", "color": "#d83b01",
     "subject": "关于规范差旅报销标准的说明",
     "content": "各位同事，为了规范财务管理，最新的差旅报销标准（V2.1版）已上传至企业知识库，下月起正式执行。"},
    {"sender": "CEO Office <ceo@company.com>", "avatar": "CE", "color": "#172b4d",
     "subject": "Q3 季度全体员工大会（Townhall）会议纪要",
     "content": "感谢大家参与昨日的季度大会。附件是会议演示文稿及业务问答纪要，请查收。"}
]

data_2_pool = [
    {"sender": "Design Team", "avatar": "D", "color": "#8e24aa", "subject": "新版官网视觉设计初稿",
     "content": "Hi，这是本周完成的新版官网设计初稿，Figma 链接已经附在下方，请查看并留下你的修改建议。"},
    {"sender": "Marketing", "avatar": "M", "color": "#e53935", "subject": "Q3 营销数据分析报告",
     "content": "各位，Q3 的营销漏斗数据已经整理完毕，整体转化率达到了预期。详细数据见附件。"},
    {"sender": "王建国 (Sales)", "avatar": "W", "color": "#43a047", "subject": "大客户A项目需求调研纪要",
     "content": "昨天下午与客户进行了初步沟通，客户对我们在安全隔离方面的能力非常感兴趣，下一步需要出具一份技术方案。"},
    {"sender": "李雪 (Product)", "avatar": "L", "color": "#1e88e5", "subject": "V2.0 版本迭代规划会议提醒",
     "content": "提醒一下各位，今天下午 3 点在 A 会议室进行下个大版本的迭代规划，请各线负责人提前准备好 Backlog。"},
    {"sender": "System Alert", "avatar": "S", "color": "#546e7a", "subject": "您的云盘空间即将使用过半",
     "content": "温馨提示：您的企业云盘当前已使用 45GB，总容量 100GB。您可以随时清理不需要的过期文件。"}
]

data_3_pool = [
    {"sender": "张三 (前端主管)", "avatar": "DEV", "subject": "修复购物车结算页面的偶发崩溃bug",
     "content": "该bug在特定的移动端浏览器下会复现，已经将报错日志附在工单中，请在周三前修复并提交测试。"},
    {"sender": "李四 (产品经理)", "avatar": "PM", "subject": "评估新版个人中心页面的开发工时",
     "content": "UI 图已经全部切好，请评估一下前后端联调需要的时间，并在周会前更新到甘特图上。"},
    {"sender": "Scrum Master", "avatar": "SM", "subject": "Code Review 提醒：认证模块重构",
     "content": "PR #402 已经提交，涉及核心的登录鉴权逻辑，请尽快安排交叉 Code Review。"},
    {"sender": "运维报警系统", "avatar": "OPS", "subject": "处理数据库慢查询告警",
     "content": "监控显示 user_activity 表存在多个执行超过 2 秒的慢查询，请配合 DBA 检查索引是否失效。"},
    {"sender": "测试团队", "avatar": "QA", "subject": "回归测试未通过：发票导出功能异常",
     "content": "在预发环境中，选择 PDF 格式导出时偶尔返回 500 错误。已抓取堆栈信息附在缺陷管理工具中。"}
]

data_4_pool = [
    {"sender": "GitLab CI", "subject": "生产环境部署成功 - v2.5.1",
     "content": "- Tests passed: 142/142<br>- Build time: 4m 12s<br>- Deployed to: Production Cluster A<br>All services are running normally."},
    {"sender": "Jenkins Auto", "subject": "定时数据备份任务已完成",
     "content": "- Database: Main_DB_Prod<br>- Size: 42.5 GB<br>- Status: Uploaded to secure S3 bucket successfully."},
    {"sender": "AWS CloudWatch", "subject": "自动扩容组(ASG)触发通知",
     "content": "- Trigger: CPU Utilization > 80% for 5 mins<br>- Action: Added 2 new EC2 instances<br>- Current Capacity: 6 instances online."},
    {"sender": "SonarQube", "subject": "静态代码扫描报告：通过",
     "content": "- Quality Gate: Passed<br>- New Bugs: 0<br>- Vulnerabilities: 0<br>- Code Smell: 12 (Minor)<br>- Coverage: 85.4%"},
    {"sender": "K8s Controller", "subject": "Pod 滚动更新完毕: Payment-Service",
     "content": "- Target image: payment-svc:v1.9.3<br>- Strategy: RollingUpdate<br>- Result: 4/4 Replicas healthy and serving traffic."}
]

data_5_pool = [
    {"sender": "王五 (部门经理)", "subject": "关于采购新一批测试服务器的申请",
     "content": "预算额度合规，准予采购。请按流程联系供应商。"},
    {"sender": "财务部", "subject": "张三的 10 月份报销单",
     "content": "票据核对无误，款项将在 3 个工作日内打入您的工资卡。"},
    {"sender": "行政部", "subject": "办公室工位调整申请单",
     "content": "已确认目标工位空闲，IT 部门将于本周五下午协助搬迁网络及电脑设备。"},
    {"sender": "法务部", "subject": "关于《第三方合作框架协议》的法务审核",
     "content": "合同核心条款已审核，责任边界清晰，无明显法律风险。可继续推进盖章流程。"},
    {"sender": "HRBP", "subject": "研发部新增前端工程师 HC 审批",
     "content": "符合年度业务发展规划及人力成本预算，同意开启招聘流程。已通知招聘专员发布 JD。"}
]

templates_library = [
    (style_1_html, data_1_pool),
    (style_2_html, data_2_pool),
    (style_3_html, data_3_pool),
    (style_4_html, data_4_pool),
    (style_5_html, data_5_pool)
]

print(f"🚀 开始生成 100 张【多风格、高差异化】的正样本邮件截图...")
print(f"📂 保存路径: {OUTPUT_DIR}")

# ==========================================
# 执行批量生成
# ==========================================

# 👇 核心：先数一数 normal 文件夹里已经有几张正常图片了
exist_count = len(os.listdir(OUTPUT_DIR))

for i in range(100):
    # 1. 随机选一种 UI 风格和其对应的语料库
    html_temp, data_pool = random.choice(templates_library)

    # 2. 从选中的语料库中随机抽取一条数据
    item = random.choice(data_pool)

    # 3. 随机生成一个逼真的过去时间
    fake_date = (datetime.now() - timedelta(minutes=random.randint(5, 5000))).strftime("%Y-%m-%d %H:%M")

    # 4. 填充 HTML 模板
    current_html = html_temp.format(
        avatar_color=item.get("color", "#000"),
        avatar_text=item.get("avatar", "SYS"),
        sender=item.get("sender"),
        subject=item.get("subject"),
        content=item.get("content"),
        date=fake_date
    )

    # 👇 自动顺延命名：接着之前的数字往下排！认准 normal_ 前缀！
    filename = f"normal_{exist_count + i + 1:03d}.png"

    try:
        hti.screenshot(html_str=current_html, save_as=filename)
    except Exception as e:
        print(f"⚠️ 第 {exist_count + i + 1} 张截图生成失败: {e}")
        continue

    if (i + 1) % 10 == 0:
        print(f"✅ 本次已完成: {i + 1} 张 (正常图库总数: {exist_count + i + 1})")

print("🎉 超丰富、无死角的正常邮件生成完毕！模型现在不会被轻易忽悠了！")