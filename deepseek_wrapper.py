from typing import List, Optional, Any, Dict
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import BaseMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.tools import BaseTool
from pydantic import Field
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_ollama import OllamaLLM
import json

class DeepseekToolWrapper(BaseChatModel):
    """Deepseek 模型的工具调用包装器，专门用于浏览器自动化任务"""
    
    ollama: OllamaLLM = Field(default=None)
    tools: List[BaseTool] = Field(default_factory=list)
    
    def __init__(
        self, 
        model_name: str = "deepseek-r1:1.5b",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.ollama = OllamaLLM(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    @property
    def _llm_type(self) -> str:
        return "deepseek_wrapper"
        
    def bindTools(self, tools: List[BaseTool]):
        self.tools = tools
        return self
    
    def _format_tool_descriptions(self) -> str:
        """格式化工具描述，添加浏览器操作相关的说明"""
        tool_descriptions = []
        for tool in self.tools:
            desc = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.schema() if tool.args_schema else None,
                "required": tool.args_schema.schema().get("required", []) if tool.args_schema else []
            }
            tool_descriptions.append(desc)
        return json.dumps(tool_descriptions, ensure_ascii=False, indent=2)
    
    def _format_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """将消息转换为提示，添加浏览器自动化相关的上下文"""
        prompt_parts = []
        
        # 添加系统说明
        prompt_parts.append("""
        你是一个专门用于浏览器自动化的AI助手。你可以：
        1. 理解和执行网页操作任务
        2. 使用提供的工具进行交互
        3. 处理页面状态和DOM元素
        4. 正确处理错误和异常情况
        """)
        
        # 添加工具说明
        if self.tools:
            prompt_parts.append("可用工具:\n" + self._format_tool_descriptions())
            prompt_parts.append("""
            使用工具时，请遵循以下格式：
            {
                "action": "工具名称",
                "params": {
                    "参数名": "参数值"
                },
                "thought": "行动原因说明"
            }
            """)
        
        # 添加消息历史
        for message in messages:
            if isinstance(message, SystemMessage):
                prompt_parts.append(f"System: {message.content}")
            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
                
        return "\n".join(prompt_parts)
    
    def _parse_response(self, response: str) -> Dict:
        """解析模型响应，确保返回正确的动作格式"""
        try:
            # 尝试解析 JSON
            action_data = json.loads(response)
            if isinstance(action_data, dict) and "action" in action_data:
                return action_data
        except:
            pass
        
        # 如果不是有效的 JSON，返回默认格式
        return {
            "action": "think",
            "thought": response,
            "params": {}
        }
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成响应并返回标准格式"""
        prompt = self._format_messages_to_prompt(messages)
        response = self.ollama.invoke(prompt)
        
        # 解析响应
        parsed_response = self._parse_response(str(response))
        
        # 创建 ChatGeneration 对象
        chat_generation = ChatGeneration(
            message=AIMessage(content=json.dumps(parsed_response, ensure_ascii=False)),
            generation_info={"parsed_response": parsed_response}
        )
        
        return ChatResult(generations=[chat_generation])
        
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """异步生成响应"""
        prompt = self._format_messages_to_prompt(messages)
        response = await self.ollama.ainvoke(prompt)
        
        # 解析响应
        parsed_response = self._parse_response(str(response))
        
        # 创建 ChatGeneration 对象
        chat_generation = ChatGeneration(
            message=AIMessage(content=json.dumps(parsed_response, ensure_ascii=False)),
            generation_info={"parsed_response": parsed_response}
        )
        
        return ChatResult(generations=[chat_generation]) 