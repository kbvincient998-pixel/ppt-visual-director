---
name: ppt-visual-director
description: 以 IMAGE2IMAGE 为核心审计、重构和美化 PowerPoint 演示文稿，并保证图文语义匹配、品牌真实性和关键内容可编辑。用于美化或重排现有 PPTX、根据 PDF/PPTX/图片参考稿建立视觉语言、把普通官方产品图或人物图改造成适配页面的主视觉、制作 3–5 张样页后批量处理全稿、检索小红书参考并生成可追溯灵感板，以及对含视频、动画或特殊对象的 PowerPoint 选择安全编辑路线。
---

# PowerPoint 视觉导演

把演示文稿美化视为“内容判断 → 视觉导演 → 素材重构 → 对象级排版 → 渲染验收”，而不是对齐、套模板或把图片塞进页面。默认约 80% 的品牌素材会先经过 IMAGE2IMAGE 或“真实主体＋生成环境”的重构，再进入 PPT。

## 不可妥协的规则

- 保留原 PPTX 和原始素材，始终输出新文件。
- 先理解页面任务，再决定图片；先确定构图和文字安全区，再处理素材。
- 用户参考稿、现有 PPTX 和品牌要求优先于任何内置模板。单个项目只采用一套主视觉语言，不混合多套参考稿的表面风格。
- 默认先完成 3–5 张不同角色的样页。用户确认视觉方向后再批量处理全稿；只有用户明确要求时才跳过样页。
- 标题、正文、关键数据、图表和主要图片框保持可编辑。复杂氛围视觉可以作为独立背景图层。
- 产品包装、Logo、色号、功效文字、人物身份和真实平台内容是真实性锚点，不得被生图模型重绘或伪造。
- 小红书只用于参考检索和灵感板。不得自动取图入稿、去水印、伪造达人笔记或把参考作品当成可用素材。
- 不得用生成图替代真实产品证据、消费者证言、平台截图、代言人照片或活动记录。

## 开始前读取

按当前任务读取所需参考：

- 任何美化任务：读 `references/visual-grammar.md`。
- 涉及品牌图片、生图或素材重构：读 `references/image2image-workflow.md`。
- 涉及小红书：读 `references/xiaohongshu-reference-workflow.md`。
- 涉及现有 PPTX、批量编辑、视频、动画或 QA：读 `references/powerpoint-execution-and-qa.md`。

同时使用系统的 `Presentations`、`imagegen`、`browser` 和 `computer-use` Skill；服从它们关于文件编辑、浏览器登录、图片编辑和界面操作的规则。

将 `SKILL_DIR` 设为本 `SKILL.md` 所在目录。优先使用 Codex 工作区提供的 Python 并设为 `PYTHON`；`build_reference_board.py` 需要 Pillow，不要假设系统 Python 已安装该依赖。

## 输入与交付

尽量从用户和项目中收集：

- 待美化 PPTX。
- PDF、PPTX、图片或现有页面参考。
- 产品图、人物图、KV、Logo、截图和其他品牌素材。
- 文案、受众、场景、品牌调性、禁用项和输出位置。
- 可选的小红书关键词。

交付：

- 样页 PPTX；确认后交付完整 PPTX。
- 最终使用的新增或重构图片资产。
- 素材来源、处理方式和真实性状态记录。
- 最终 QA 结论；如存在无法安全保留的特殊对象，明确指出。

## 工作流

### 1. 全稿预检

1. 运行：

   ```bash
   "$PYTHON" "$SKILL_DIR/scripts/audit_pptx.py" "<input.pptx>" --out "<audit.json>"
   ```

2. 渲染并检查全部页面，不只抽样封面。
   - 大文件一次渲染发生内存不足或导出失败时，按页段分批渲染。
   - 若项目中已有同版本、同页数 PDF，可作为静态视觉代理；必须核对页数和代表页内容。
   - PDF 代理只能用于视觉学习和静态 QA，不能证明视频、动画、转场或可编辑对象完整。
3. 检查母版、字体、图表、表格、分组、音视频、动画、嵌入对象和页面尺寸。
   - 对照审计结果检查引用字体是否在当前电脑安装；没有嵌入字体时，字体缺失会改变换行和版式。
4. 将每页标为：
   - `native-editable`：原生文字、图片框、图表等可安全重排。
   - `composite-visual`：复杂拼贴或氛围视觉，需保持整体关系。
   - `media-protected`：含视频、动画、转场或特殊对象，优先保守编辑。
   - `evidence-protected`：真实截图、数据或证言，不可生成替代。

脚本只给出 `native-editable`、`composite-visual` 和 `media-protected` 的技术初判。`evidence-protected` 必须通过页面视觉和语义人工确认，不能仅凭 XML 猜测。

### 2. 判断页面角色

每页只能有一个首要角色：

- `emotion`：封面、章节、宣言和情绪转场。
- `product`：产品利益、卖点和产品故事。
- `insight`：市场、受众和策略洞察。
- `evidence`：数据、截图、案例和消费者证据。
- `idea`：Big Idea、概念、核心主张和主视觉。
- `mechanism`：活动机制、内容玩法和执行链路。
- `summary`：阶段总结、路线图和收束。

先写出该页唯一主结论，再选择版式。不要让同一页同时承担多个主任务。

### 3. 提炼参考稿视觉 DNA

记录：

- 主色、辅助色、材质、明暗和图像颗粒。
- 标题、正文、数字和注释的字号与字重层级。
- 网格、留白、出血、裁切、叠层和页面边界处理。
- 情绪页与证据页的密度变化。
- 图片主体与文字落位的固定关系。
- 可重复使用的品牌签名元素。

不要复制单页外观。把视觉规则映射到页面角色，再生成新的页面。

### 4. 为每个视觉建立任务单

为所有需要新增或重构的图片建立 JSON 任务单，并运行：

```bash
"$PYTHON" "$SKILL_DIR/scripts/validate_visual_tasks.py" "<visual-tasks.json>"
```

最低结构：

```json
{
  "tasks": [{
    "slide": 6,
    "role": "product",
    "message": "修护力要在第一眼被看懂",
    "asset_mode": "preserve-cutout-composite",
    "source_assets": ["product-packshot.png"],
    "input_image_roles": {
      "product-packshot.png": "edit-target"
    },
    "invariants": ["产品瓶身像素", "Logo", "包装文字", "色号"],
    "target": {
      "aspect_ratio": "16:9",
      "subject_position": "right",
      "text_safe_zone": "left 38%"
    },
    "visual_language": {
      "target_brand": "当前品牌",
      "reference_policy": "其他品牌参考只用于构图和材质，不迁移 Logo、包装或品牌身份"
    },
    "allowed_changes": ["背景", "环境光", "接触阴影", "反射", "景深"],
    "forbidden": ["重绘产品", "伪文字", "错误 Logo", "水印"]
  }]
}
```

### 5. 动态选择素材路线

按“真实性要求 × 视觉适配度”选择：

| 状态 | 路线 |
| --- | --- |
| 真实且视觉成熟 | `direct-use` 或 `light-edit` |
| 真实但不适合版式 | `image2image-edit` |
| 产品必须绝对准确 | `preserve-cutout-composite` |
| 代言人或官方人物 | `identity-preserve` |
| 达人笔记、证言、平台页面 | `evidence-preserve` |
| 概念氛围、抽象场景 | `generate-new` |
| 低清或无使用权素材 | 仅作参考，重新制作 |

### 6. 执行 IMAGE2IMAGE

默认使用内置 `image_gen`：

1. 本地素材先用 `view_image` 检查。
2. 明确标注每张输入图是“编辑目标、风格参考或合成素材”。
3. 当参考图来自其他品牌时，明确写出目标品牌与隔离规则；只借鉴构图、光线、材质或镜头语言，不迁移 Logo、包装、产品身份或专属品牌符号。
4. 提示词先写页面用途、画幅、主体位置和文字安全区，再写场景、光影和材质。
5. 每次都重复不可改变项；一次迭代只改一个变量。
6. 产品页优先生成不含产品的环境，再把真实产品抠图作为独立图层放回 PPT；这比让模型重绘产品更可靠。
7. 透明、玻璃、液体、毛发或强反光主体需要真实透明时，遵循 `imagegen` Skill 的透明背景规则；需要 CLI 回退时先征得用户同意。
8. 所有项目内会使用的最终图片复制到项目工作区，不只留在生成缓存目录。

详细规则见 `references/image2image-workflow.md`。

为每个进入成稿的新图片维护 `asset-manifest.json`，至少记录：

- 输出文件、使用页码和页面角色。
- 原始素材路径或来源 URL。
- 来源类型：用户、品牌官方、已授权、生成或 `reference-only`。
- 编辑方式、不可改变项和最终提示词。
- 权利状态与产品/人物保真 QA 结论。

小红书 `reference-only` 候选不得出现在成稿资产列表中。

### 7. 可选的小红书灵感板

仅在用户要求或参考不足时执行：

1. 用已有登录态浏览器进行站内搜索。
2. 收集约 12 个候选，不批量抓取。
3. 保存缩略图和元数据，运行：

   ```bash
   "$PYTHON" "$SKILL_DIR/scripts/build_reference_board.py" \
     "<candidates.json>" \
     --board "<reference-board.png>" \
     --ledger "<source-ledger.md>"
   ```

4. 给出推荐理由和可借鉴的构图，不直接复制作品。
5. 登录、验证码或权限受阻时交由用户完成；不绕过限制。

### 8. 制作样页

从实际全稿中选择 3–5 页，尽量覆盖：

- 封面或情绪页。
- 产品主视觉页。
- 策略或洞察页。
- 达人、截图或证据页。
- 机制或执行页。

样页必须同时验证：视觉语言、IMAGE2IMAGE 处理尺度、产品保真、文字层级、可编辑性和整套节奏。用户确认前不要批量铺开。

### 9. 批量编辑 PowerPoint

- 无高风险媒体时，使用 `Presentations` Skill 要求的 `@oai/artifact-tool` 编辑 PPTX。
- 检测到视频、动画、宏、OLE、特殊转场或导入导出不兼容时，不让整份文件经过可能丢失对象的往返；改用 PowerPoint 界面在副本中编辑。
- 文件级处理负责速度，界面级处理只补文件接口覆盖不到的能力。
- 不覆盖源文件，不用扁平整页图片遮盖可编辑内容。

### 10. QA 与交付

1. 渲染每一页并逐页查看全尺寸结果。
2. 检查文字溢出、错误换行、裁切、遮挡、图片清晰度、色彩、产品边缘和页面节奏。
3. 对产品图做原图与成图对照；Logo、包装文字、色号或形态漂移即失败。
4. 对媒体复杂文件运行：

   ```bash
   "$PYTHON" "$SKILL_DIR/scripts/compare_pptx_media.py" "<source.pptx>" "<final.pptx>"
   ```

5. 验证标题、正文、数据、图表和主要图片框仍可编辑。
6. 最终文件使用新名称，并报告素材来源和所有保守处理项。

## 资源

- `references/visual-grammar.md`：页面角色、视觉语法和图文匹配。
- `references/image2image-workflow.md`：以产品保真为核心的图片重构流程。
- `references/xiaohongshu-reference-workflow.md`：小红书灵感板和来源规则。
- `references/powerpoint-execution-and-qa.md`：文件编辑、界面兜底和 QA。
- `scripts/audit_pptx.py`：PPTX 媒体与对象风险审计。
- `scripts/validate_visual_tasks.py`：视觉任务单校验。
- `scripts/build_reference_board.py`：12 图灵感板与来源清单。
- `scripts/compare_pptx_media.py`：源文件与成稿媒体完整性比对。
