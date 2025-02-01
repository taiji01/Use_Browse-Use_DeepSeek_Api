import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional
# 新增导入项
from browser_use.agent.views import ActionResult
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from browser_use import Agent, Browser, BrowserConfig

# ---------------------------
# 第一部分：环境配置
# ---------------------------
# 加载.env文件中的敏感信息
load_dotenv()

# 获取DeepSeek API密钥（需在.env中设置）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")

# ---------------------------
# 第二部分：浏览器配置
# ---------------------------
def configure_edge_browser() -> Browser:
    """配置Edge浏览器实例"""
    edge_path = None

    # 自动检测常见安装路径（Windows）
    possible_paths = [
        # Windows 默认安装路径
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # MacOS 路径（如有需要）
        # "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]

    # 寻找存在的Edge可执行路径
    for path in possible_paths:
        if Path(path).exists():
            edge_path = path
            break

    if not edge_path:
        raise FileNotFoundError("未找到Microsoft Edge安装路径")

    return Browser(
        config=BrowserConfig(
            chrome_instance_path=edge_path,  # 关键配置：指定Edge路径
            headless=False,  # 显示浏览器界面
            #slow_mo=500,     # 操作间隔500ms（方便观察）
            timeout=30000,   # 超时30秒
        )
    )

# ---------------------------
# 第三部分：登录凭证处理
# ---------------------------
async def handle_login(context, url: str) -> Optional[ActionResult]:
    """智能登录处理模块"""
    # 从环境变量获取凭证（安全方式）
    username = os.getenv("SITE_USERNAME")
    password = os.getenv("SITE_PASSWORD")

    if not (username and password):
        return None  # 无凭证时跳过

    # 构造自然语言登录指令
    login_task = f"""
    在 {url} 执行登录操作：
    1. 找到用户名输入框，输入：{username}
    2. 找到密码输入框，输入：{password}
    3. 找到登录按钮并点击
    确保成功登录后再继续后续操作
    """

    # 创建临时Agent处理登录
    login_agent = Agent(
        task=login_task,
        llm=ChatOpenAI(
            base_url="https://api.deepseek.com/v1",
            model="deepseek-reasoner",
            openai_api_key=SecretStr(DEEPSEEK_API_KEY),
        ),
        browser=context.browser,
        parent_context=context,
    )
    
    return await login_agent.run()

# ---------------------------
# 第四部分：主程序
# ---------------------------
async def main():
    # 初始化配置好的Edge浏览器
    edge_browser = configure_edge_browser()

    try:
        # 创建主Agent
        agent = Agent(
            task="在bilibili上搜索'AI-ToolKit',找到对应用户,然后进入用户主页,播放播放量最高的视频,等待视频播放完毕",
            llm=ChatOpenAI(
                base_url="https://api.deepseek.com/v1",
                model="deepseek-reasoner",
                openai_api_key=SecretStr(DEEPSEEK_API_KEY),
                temperature=0.3,
            ),
            browser=edge_browser,
            # 注入登录处理钩子
            context_hooks={"before_navigation": handle_login}
        )

        # 执行任务
        result = await agent.run()
        print("\n任务结果：", result)

    finally:
        await edge_browser.close()  # 确保关闭浏览器

if __name__ == "__main__":
    asyncio.run(main())