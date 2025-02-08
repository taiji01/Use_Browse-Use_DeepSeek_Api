import os
import asyncio
from pathlib import Path
from browser_use import Agent, Browser, BrowserConfig
from langchain_ollama import ChatOllama
from deepseek_wrapper import DeepseekToolWrapper

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

#根据需要选择使用qwen还是deepseek
'''
llm1=ChatOllama(
                model="qwen2:7b",  # 使用本地 Ollama 模型
                num_ctx=32000  # 增加上下文窗口，防止任务过长被截断
            )
'''
llm2=DeepseekToolWrapper()
'''
llm3=llm1=ChatOllama(
                model="MFDoom/deepseek-r1-tool-calling:7b",  # 使用本地 Ollama 模型
                num_ctx=32000  # 增加上下文窗口，防止任务过长被截断
            )
'''
async def main():
    # 1. 初始化浏览器
    browser = configure_chrome_browser()
    
    try:
        # 2. 初始化模型
        model = llm2
        
        # 3. 创建Agent实例
        agent = Agent(
            task="""
            1. 在导航栏中输入网址bilibili.com，进入网页
            2. 在 bilibili.com 执行以下操作：
            3. 在搜索栏输入 'AI-ToolKit'
            4. 切换到用户标签页
            5. 点击第一个用户结果
            6. 进入用户主页后点击'视频'选项卡
            7. 播放最新发布的视频
            8. 等待15秒后返回视频标题和播放时长
            """,
            llm=model,
            browser=browser
        )
        
        # 4. 执行任务
        result = await agent.run()
        print("\n执行结果：", result)
        
    finally:
        # 5. 确保关闭浏览器
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
