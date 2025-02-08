# 📌 项目说明

本项目包含多个测试文件，其中 `test2.py` 和 `localTest2.py` 可正常运行。

📅 **2025/2/8 更新**：
- **新增** `main.py`。
- **修改** `localTest2.py`，支持 DeepSeek 本地模型的工具调用。

---

## 🚀 运行说明

### 📝 `test2.py`
- 使用 **DeepSeek API** 进行推理。
- 运行前，请在 `.env` 文件中添加 **API 密钥**。

### 🖥️ `localTest2.py`
- 使用本地部署的 **Qwen 7B** 模型进行推理。
- **2025/2/8 更新**：
  1. **DeepSeek 本地模型支持工具调用**
     - 通过 `deepseek_wrapper.py` 实现包装器，使其支持工具调用。
     - 在 `main.py` 中成功测试工具调用。
     - 但 `browser use` 功能无法正常工作。
  2. **直接使用新版 DeepSeek 本地模型**：
     - 采用 `deepseek-r1-tool-calling:7b` 版本。
     - 本地运行模型并使用 `browser use`，相关代码位于 `localTest2.py`。

---

## ⚠️ 注意事项

- **其他文件** 仅用于测试和实验。
- **运行 `test2.py` 前**，请确保 API 密钥已正确配置。
- **本地运行 `localTest2.py` 前**，需提前部署 **Qwen 7B** 模型。

📖 如有问题，请参考相关文档或联系项目作者。


