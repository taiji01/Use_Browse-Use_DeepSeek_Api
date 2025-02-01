import os
import asyncio
from pathlib import Path
from browser_use import Agent, Browser, BrowserConfig
from langchain_ollama import ChatOllama

def configure_chrome_browser() -> Browser:
    """配置 Chrome 浏览器实例"""
    chrome_path = None
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/opt/google/chrome/chrome",
    ]

    for path in possible_paths:
        if Path(path).exists():
            chrome_path = path
            break

    if not chrome_path:
        raise FileNotFoundError(
            "未找到Google Chrome，请确认已安装最新版本，并修改路径"
        )

    return Browser(
        config=BrowserConfig(
            chrome_instance_path=chrome_path,  
        )
    )

async def main():
    # 初始化本地 Chrome 浏览器
    chrome_browser = configure_chrome_browser()

    try:
        # 创建 AI 代理
        agent = Agent(
            task=(
                "1.输入网址bilibili.com，进入网页\n"
                "2.在 bilibili.com 执行以下操作：\n"
                "3.在搜索栏输入 'AI-ToolKit'\n"
                "4.切换到用户标签页\n"
                "5.点击第一个用户结果\n"
                "6.进入用户主页后点击'视频'选项卡\n"
                "7.播放最新发布的视频\n"
                "8.等待15秒后返回视频标题和播放时长"
            ),
            llm=ChatOllama(
                model="qwen2:7b",  # 使用本地 Ollama 模型
                num_ctx=32000  # 增加上下文窗口，防止任务过长被截断
            ),
            browser=chrome_browser,
            use_vision=False,
            max_failures=3,
            max_actions_per_step=2
        )

        # 运行任务
        result = await agent.run()
        print(f"\n执行结果：{result}")

    finally:
        await chrome_browser.close()

if __name__ == "__main__":
    asyncio.run(main())
