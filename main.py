from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_openai_tools_agent
from deepseek_wrapper import DeepseekToolWrapper
from typing import Optional, Type

# 定义一些示例工具
class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "用于执行基本数学计算"
    
    def _run(self, query: str) -> str:
        try:
            return str(eval(query))
        except:
            return "计算错误"
            
    async def _arun(self, query: str) -> str:
        return self._run(query)

def main():
    # 初始化包装后的模型
    model = DeepseekToolWrapper()
    
    # 定义工具列表
    tools = [CalculatorTool()]
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手，可以使用提供的工具来完成任务。"),
        ("human", "{input}"),
        ("assistant", "让我来帮你完成这个任务。"),
        ("human", "{agent_scratchpad}"),
    ])
    
    # 创建agent
    agent = create_openai_tools_agent(
        llm=model,
        tools=tools,
        prompt=prompt
    )
    
    # 创建执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )
    
    # 测试
    result = agent_executor.invoke(
        {"input": "计算23+45是多少?"}
    )
    print("结果:", result)

if __name__ == "__main__":
    main() 