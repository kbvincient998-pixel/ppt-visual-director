# PPT Visual Director

一个以 IMAGE2IMAGE 为核心的 Codex PowerPoint 视觉导演 Skill。

它不是简单的自动对齐工具，而是将 PPT 美化拆成：

`页面角色判断 → 参考稿视觉 DNA → 构图任务单 → 素材真实性分级 → IMAGE2IMAGE/合成 → 样页确认 → 批量排版 → 逐页 QA`

## 核心能力

- 根据 PDF、PPTX 或图片参考稿学习视觉语言。
- 识别情绪、产品、洞察、证据、创意、机制和总结页面。
- 将普通品牌官方素材作为真实性锚点，重构背景、光影、构图、材质和文字留白。
- 默认锁定产品包装、Logo、文字、色号和人物身份。
- 优先使用“真实产品抠图＋生成环境＋PPT 分层合成”，避免模型重绘产品。
- 先制作 3–5 张样页，确认后再批量处理全稿。
- 为小红书/社交内容候选生成灵感板与来源清单，默认仅供参考。
- 审计 PPTX 的视频、动画、转场、字体、母版、表格和嵌入对象。
- 比对编辑前后的音视频、动画、转场和嵌入对象完整性。

## 安装

### 让 Codex 安装

把下面这句话发给 Codex：

```text
请从 https://github.com/kbvincient998-pixel/ppt-visual-director/tree/main/ppt-visual-director 安装 ppt-visual-director Skill
```

### 使用官方 Skill Installer

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo kbvincient998-pixel/ppt-visual-director \
  --path ppt-visual-director
```

安装后，在新的 Codex 任务中调用：

```text
使用 $ppt-visual-director 美化这份 PPT，参考我提供的方案，先做 5 张样页。产品本体严格保真。
```

## 典型输入

- 待美化的 `.pptx`。
- PDF、PPTX、图片参考稿。
- 品牌产品图、人物图、KV、Logo 和平台截图。
- 文案、品牌调性、禁用项和可选的小红书关键词。

## 使用原则

- 不覆盖原始 PPTX 或品牌素材。
- 不用生成图伪造产品证据、达人笔记、消费者证言或平台数据。
- 小红书素材默认标记为 `reference-only`，不自动取图入稿。
- 标题、正文、数据、图表和主要图片框尽量保持可编辑。
- 媒体复杂文件优先通过 PowerPoint 原生界面编辑，避免视频和动画丢失。

## 运行环境

- Codex。
- PowerPoint 工作流建议在安装 Microsoft PowerPoint 的环境中运行。
- 灵感板脚本需要 Python 与 Pillow。
- 图片编辑使用 Codex 内置 `image_gen` 能力。
- PPTX 文件级编辑遵循 Codex `Presentations` Skill 的运行要求。

## 仓库内容

```text
ppt-visual-director/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
```

仓库不包含任何品牌提案、客户文件、参考 PDF/PPTX 或受版权保护的示例素材。

## License

MIT
