import dotenv
from langchain.tools import tool
from langchain.tools.render import render_text_description
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# 加载环境变量
dotenv.load_dotenv()


# 定义一个乘法工具
@tool
def multiply(first: int, second: int) -> int:
    """实现两个整数的乘法运算。"""
    return first * second


# 定义一个加法工具
@tool
def add(first: int, second: int) -> int:
    """实现两个整数的加法运算。"""
    return first + second


# 定义一个指数运算工具
@tool
def exponentiate(base: int, exponent: int) -> int:
    """实现指数运算。"""
    return base**exponent


# 可用工具列表
tools = [multiply, add, exponentiate]


# 根据输入链式调用工具的函数
def tool_chain(input):
    # 将工具名称映射到工具函数
    tool_map = {tool.name: tool for tool in tools}
    # 根据输入名称选择工具
    choose_tool = tool_map[input["name"]]
    # 拷贝输入参数
    arguments = input["arguments"].copy()
    for key, value in arguments.items():
        # 如果值是字典，递归调用tool_chain
        if isinstance(value, dict):
            arguments[key] = tool_chain(value)
    # 使用参数调用选定的工具
    return choose_tool.invoke(arguments)


# 渲染工具的文本描述
rendered_tools = render_text_description(tools)

# 定义系统提示
system_prompt = f"""你是一个可以访问以下工具集的助手。以下是每个工具的名称和描述：

{rendered_tools}

根据用户输入，返回要使用的工具的名称和输入。将你的响应以包含 'name' 和 'arguments' 键的 JSON 格式返回。"""

# 从系统和用户消息创建聊天提示模板
prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", "{input}")]
)

# 创建ChatOpenAI模型
model = ChatOllama(model="deepseek-r1:1.5b", temperature=0)

# 链接提示、模型、JSON输出解析器和工具链
chain = (
    prompt | model | JsonOutputParser() | RunnablePassthrough.assign(result=tool_chain)
)

# 使用特定输入调用链并打印输出
result = chain.invoke({"input": "计算 13 乘以 4 的结果的平方"})
print(result)