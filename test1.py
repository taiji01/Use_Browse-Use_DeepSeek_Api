import os
import asyncio
from pathlib import Path
from typing import Optional
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

# ---------------------------
# Edge浏览器配置模块
# ---------------------------
def configure_edge_browser() -> Browser:
    """自动检测并配置Edge浏览器实例"""
    edge_path = None
    
    # Windows系统常见安装路径
    possible_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # MacOS路径（如需）
        # "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]

    # 自动检测有效路径
    for path in possible_paths:
        if Path(path).exists():
            edge_path = path
            break

    if not edge_path:
        raise FileNotFoundError(
            "Edge浏览器未找到，请确认已安装Microsoft Edge\n"
            "或手动指定安装路径：https://learn.microsoft.com/zh-cn/microsoft-edge/"
        )

    return Browser(
        config=BrowserConfig(
            chrome_instance_path=edge_path,  # 关键配置
            #headless=False,    # 显示浏览器界面
            #timeout=15000,     # 超时15秒
            # 注意：当前版本可能不支持slow_mo参数
        )
    )

# ---------------------------
# 主程序逻辑
# ---------------------------
async def main():
    # 初始化浏览器
    edge_browser = configure_edge_browser()

    try:
        # 创建智能体
        agent = Agent(
            task=(
                "在 bilibili.com 执行以下操作：\n"
                "1. 访问主页\n"
                "2. 在搜索栏输入 'AI-ToolKit'\n"
                "3. 选择用户标签\n"
                "4. 进入用户主页\n"
                "5. 点击'主頁'选项卡\n"
                "6. 选择最新发布的视频播放\n"
                "7. 等待10秒后返回视频标题"
            ),
            llm=ChatOpenAI(
                model="gpt-4o",
                temperature=0.3  # 降低随机性
            ),
            browser=edge_browser,
        )

        # 执行任务
        result = await agent.run()
        print(f"\n任务执行结果：{result}")

    finally:
        await edge_browser.close()  # 确保关闭浏览器

if __name__ == "__main__":
    # 异步执行入口
    asyncio.run(main())