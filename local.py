import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_ollama import ChatOllama  # 使用本地 Ollama 模型
from browser_use import Agent, Browser, BrowserConfig
from pydantic import SecretStr

# 加载环境变量
load_dotenv()

def configure_chrome_browser() -> Browser:
    """配置Chrome浏览器实例"""
    chrome_path = None
    possible_paths = [
        # Windows 路径
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # MacOS 路径
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Linux 路径
        "/usr/bin/google-chrome",
        "/opt/google/chrome/chrome",
    ]

    # 检测有效路径
    for path in possible_paths:
        if Path(path).exists():
            chrome_path = path
            break

    if not chrome_path:
        raise FileNotFoundError(
            "未找到Google Chrome安装路径，请确认：\n"
            "1. 已安装最新版Chrome\n"
            "2. 如果使用自定义安装路径，请手动指定"
        )

    return Browser(
        config=BrowserConfig(
            chrome_instance_path=chrome_path,  # 关键配置
        )
    )

async def main():
    # 初始化浏览器
    chrome_browser = configure_chrome_browser()

    try:
        # 创建智能体，使用本地 Ollama 模型
        agent = Agent(
            task=(
                "在 bilibili.com 执行以下操作：\n"
                "1. 在搜索栏输入 'AI-ToolKit'\n"
                "2. 切换到用户标签页\n"
                "3. 点击第一个用户结果\n"
                "4. 进入用户主页后点击'视频'选项卡\n"
                "5. 播放最新发布的视频\n"
                "6. 等待15秒后返回视频标题和播放时长"
            ),
            llm=ChatOllama(
                model="qwen2:0.5b",  # 使用本地模型，确保你已下载并启动
                num_ctx=32000
            ),
            browser=chrome_browser,
            use_vision=False,
            max_failures=3,
            max_actions_per_step=2
        )

        # 执行任务
        result = await agent.run()
        print(f"\n执行结果：{result}")

    finally:
        await chrome_browser.close()

if __name__ == "__main__":
    asyncio.run(main())
