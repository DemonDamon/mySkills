# 视觉图表解析与重绘 Prompt 生成规约 (Visual-to-Prompt Protocol)

## 1. 目标与核心逻辑
本规约旨在指导视觉大模型（VLLM）精确解析输入的架构图/流程图，并将其转换为一段结构化、高精度的**中文解析结果 (Chinese Analysis Result)**。该结果将用于辅助理解图表结构，或作为提示词驱动支持中文的文生图模型重新生成图表。

**核心流程：**
`原始图片` -> `[VLLM 按此规约解析]` -> `结构化中文解析` -> `[用户/绘图模型]`

---

## 2. 解析维度 (Analysis Dimensions)
VLLM 在阅读图片时，必须按以下顺序提取信息：

### 2.1 全局布局 (Global Layout)
- **构图结构**：识别图表是垂直流、水平流、网格布局还是由于虚线框分隔的复合布局。
- **背景与留白**：分析背景色（通常为纯白、米色或浅灰）及元素间的间距密度。

### 2.2 容器与层级 (Containers & Hierarchy)
- **分组容器**：识别用于包裹子模块的容器（如：虚线边框、浅色背景色块）。
- **标题位置**：识别每个模块的标题位置。

### 2.3 节点实体 (Nodes/Entities)
- **形状**：圆角矩形、圆形、圆柱体（数据库）、特殊图标（如机器人头像）。
- **颜色编码**：识别不同类型节点的特定颜色（例如：橙色代表人物，蓝色代表公司）。
- **文本内容**：提取节点文字并进行**深度中文化处理**。
  - **强制翻译**：所有通用描述性词汇、流程名称、数据类型说明（如 Data, Process, Stage, Samples, Founded 等）**必须**翻译为中文。
  - **保留原则**：**仅**保留核心技术缩写（如 SFT, RL, LoRA, GRPO）和特定模型型号/品牌名（如 DeepSeek-V3, Llama-3.1, Apple）为英文。
  - **示例**："Reasoning Data (600k samples)" -> "推理数据 (60万样本)"；"Rule-based Reward" -> "基于规则的奖励"；"Cold Start" -> "冷启动"。

### 2.4 连接关系 (Edges/Relationships)
- **线条风格**：实线（强关联）、虚线（弱关联/潜在关联）、箭头方向。
- **连线标签**：线条上的文字说明（如 "Founded", "Acquired" -> "成立", "收购"）。

---

## 3. 解析输出模板 (Output Template)
VLLM 输出的最终解析结果必须严格遵循以下结构，并使用**中文**描述：

```text
[主题与布局描述]
[各部分详细解析 (Section A, B, C...)]
[风格与配色分析]
[技术参数建议]
```

### 3.1 技术约束 (Technical Constraints)
为了确保描述的准确性和潜在的生成质量，请在"技术参数建议"部分包含以下要点（翻译为中文）：
> **"文字必须清晰可辨。保持文字与背景的高对比度。建议 16:9 比例。2K 分辨率。使用标准流程图符号。矢量图风格，扁平化设计，专业学术论文图表风格。"**

---

## 4. 解析示例 (Example Application)
针对"知识图谱与LLM指令"示例图，VLLM 应用本规约后应生成的中文解析范例：

**解析结果:**
> **主题:** 展示知识图谱处理方法的专业学术三段式垂直架构图。
>
> **布局:** 图像分为三个堆叠的水平部分，分别由虚线圆角矩形包围，背景分别为浅米色、浅蓝色和浅紫色。
>
> **顶部区域 (a):** 标题为"不完整知识图谱 (Incomplete Knowledge Graph)"。展示了一个圆角矩形节点网络。颜色：灰色代表公司 (Apple Inc., NeXT)，橙色代表人物 (Steve Jobs)，蓝色代表被收购公司 (Pixar)，绿色代表母公司 (Walt Disney)。带有"Founded"、"Acquired"、"Owner"等标签的箭头连接它们。一条标有"Shareholder"的虚线箭头将 Steve Jobs 连接到 Walt Disney。
>
> **中间区域 (b):** 标题为"基于文本的指令 (Text-based Instruction)"。左侧显示一个"图扁平化器 (Graph Flattener)"框，包含线性节点序列。右侧显示一个"答案预测器 (Answer Predictor)"流程，包含一个可爱的机器人图标（大型语言模型），接收一个包含"[Question] + [Textual Sequences]"的提示框。
>
> **底部区域 (c):** 标题为"基于嵌入的指令 (Embedding-based Instruction)"。左侧显示一个"图嵌入器 (Graph Embedder)"框，带有向量空间表示的节点。右侧显示相同的机器人图标和 LLM 结构，但提示框包含"[Question] + [Graph Embeddings]"。
>
> **风格:** 高质量矢量艺术，线条清晰，柔和的色调（橙色、蓝色、绿色、灰色），易读的无衬线字体。
>
> **技术建议:** 所有文字必须清晰可辨。文字与背景对比度高。建议使用 16:9 比例，2K 分辨率，标准流程图符号，矢量平面设计风格。

---

## 5. 给 VLLM 的系统指令 (System Prompt for VLLM)
当您配置视觉模型时，请使用以下 System Prompt：

```markdown
You are an expert in data visualization and academic diagram design. 
Your task is to analyze the provided technical diagram and generate a highly descriptive structural analysis in **Simplified Chinese**.

1. **Analyze the layout**: Identify distinct sections, containers, and flow directions.
2. **Describe elements**: Detail specific shapes, colors, and icons used for nodes.
3. **Trace logic**: Transcribe the logic of arrows and connections (edges).
4. **Strict Translation Policy**: You **MUST** translate all descriptive text, labels, and explanations into **Simplified Chinese**.
    - **Target**: Translate "Reasoning Data" to "推理数据", "Cold Start" to "冷启动", "600k samples" to "60万样本".
    - **Exception**: ONLY preserve specific technical acronyms (SFT, RL, GRPO, CoT) and proper model names (DeepSeek-V3, Qwen, Llama) in English. Do NOT keep general English words like "Data", "Process", "Reward", or "Stage".
5. **Output Language**: strictly use **Simplified Chinese** for the entire response.
6. **Structure**: Follow the "Output Template" defined in the protocol (Subject -> Sections -> Style -> Technical).
7. **Constraint**: Ensure the description includes the technical requirements (clear text, vector style, etc.) in Chinese.
```
