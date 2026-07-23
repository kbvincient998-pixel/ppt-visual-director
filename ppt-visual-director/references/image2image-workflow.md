# IMAGE2IMAGE 视觉导演流程

## 目标

把官方素材视为真实性锚点，而不是默认成稿。先为页面设计构图，再通过编辑、生成和合成得到适配 16:9 PPT 的视觉。

## 素材分级

| 级别 | 处理 |
| --- | --- |
| L0 保持 | 原图已成熟，只裁切、调色或放入版式 |
| L1 清理 | 去杂物、扩边、统一色调、改善清晰度 |
| L2 视觉导演 | 重构背景、光影、反射、景深、构图和材质 |
| L3 重新生成 | 仅用于非真实性主体、概念氛围和创意隐喻 |

L2 是默认主路径。产品、Logo、包装文字、人物身份和真实证据不得进入 L3。

## 产品锁定流程

1. 检查原图分辨率、包装文字、透明/反光边缘和品牌色。
2. 把产品本体定义为不可改变项。
3. 根据页面先确定画幅、主体位置、相机角度感和文字安全区。
4. 优先生成不含产品的新环境。
5. 对原产品做高质量抠图或保留其原始矩形区域。
6. 在 PPT 中以独立图层合成真实产品、背景、接触阴影和必要反射。
7. 对比原图；包装、Logo、色号、比例或结构发生漂移即失败。

对于玻璃、液体、透明盖、镀铬和强反射材质，不要依赖粗糙自动抠图。允许保留原始背景的局部光学信息，或让用户确认更高质量的透明处理路径。

## 人物锁定流程

- 官方人物和代言人使用 `identity-preserve`。
- 锁定面部、发型、身体特征、服装品牌元素和姿态。
- 只调整背景、色调、环境光、画幅扩展和非身份性细节。
- 任何面部漂移、肢体错误或服装 Logo 变化都必须废弃。

## 提示词结构

```text
Use case: <precise-object-edit | identity-preserve | compositing | ads-marketing>
Asset type: PowerPoint slide visual
Primary request: <只改变什么>
Input images: <Image 1: 编辑目标；Image 2: 风格参考>
Target brand: <当前要服务的品牌>
Reference policy: <其他品牌参考只用于哪些视觉特征，明确禁止迁移什么>
Scene/backdrop: <环境>
Subject: <主体>
Composition/framing: 16:9；主体在右侧；左侧 38% 保持干净
Lighting/mood: <光线和情绪>
Color palette: <品牌色与限制>
Constraints: 保持产品/人物的明确不变量
Avoid: 伪文字、错误 Logo、包装变形、水印、无关物体
```

每次迭代都重复不变量。一次只调整背景、构图、光线或材质中的一个主要变量。

任务单中的每张输入图必须使用以下角色之一：

- `edit-target`：允许在不变量约束下编辑的目标图。
- `style-reference`：只参考构图、光线、材质或情绪。
- `supporting-insert`：后期合成的辅助真实素材。
- `evidence`：不可生成修改的截图、数据或证明材料。

## 生成策略

- 草案阶段可为关键主视觉生成 2 个构图方向，选择后再精修。
- 不用 `n` 代替不同提示词；不同方向分别调用。
- 文字尽量保留为 PPT 原生文字，不让图片模型生成长文案。
- 若画面必须包含短文字，逐字提供并单独检查。
- 图片进入 PPT 前检查实际裁切区域，而不是只看原图。
- 项目最终使用的图片必须复制到项目工作区并使用版本化文件名。

## QA

- 主体位置是否为文案留出真正可用的区域。
- 产品是否与原图一致。
- 接触阴影、反射和透视是否让产品“落地”。
- 背景是否强化卖点，而非仅仅漂亮。
- 是否出现 AI 伪文字、错误手指、奇怪反射或重复物体。
- 图片在幻灯片实际尺寸下是否清晰。

## 资产记录

最终采用的每张图片都写入 `asset-manifest.json`：

```json
{
  "output_asset": "assets/slide-06-product-hero-v2.png",
  "slide": 6,
  "role": "product",
  "source_assets": ["official/product-packshot.png"],
  "source_type": "brand-official",
  "transformation": "真实产品抠图＋生成环境＋PPT 分层合成",
  "invariants": ["包装", "Logo", "色号", "瓶身比例"],
  "rights_status": "user-provided-brand-asset",
  "prompt": "最终使用的完整提示词",
  "qa": "pass"
}
```

小红书灵感板中的 `reference-only` 候选只进入来源清单，不进入成稿资产清单。
