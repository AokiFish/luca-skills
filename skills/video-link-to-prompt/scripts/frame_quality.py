#!/usr/bin/env python3
"""帧级视觉评估：清晰度 + 帧间差异。仅依赖 Pillow（无需 numpy/opencv）。

为什么需要它 —— 关键帧与分镜的专业语义要求：

- keyframe（关键帧）= 定义动作/形变「起止状态」的关键画面，控制叙事内容whatiably的关键画面。
  它必须**清晰且具备信息量**；运动模糊的中间帧恰恰是最不该被选中的一类。
  因此选帧必须先做清晰度筛查，而不是「抽某个时间点的帧」。

- storyboard（分镜）= 前期叙事/拍摄规划的规划单位，**不等于视频里的硬切数**。
  一镜到底的段落同样要按「动作节拍 / 景别·机位·视点变化」继续拆成多个 board；
  把 30s 视频硬切成「1 个镜头 = 1 个 board」是剪辑层概念错配到叙事层。

本模块提供从「画面内容」出发的度量，供上述两者使用：
- sharpness：Laplacian 方差（越高越清晰；运动模糊会显著偏低）
- contrast ：灰度标准差（画面信息量；黑场 / 纯色画面接近 0）

注意：仅靠 sharpness 无法排除黑场帧 —— 一张纯黑图的 Laplacian 方差不一定最低，
但它「几乎没有内容」。所以选代表帧 / 关键帧时，必须先用 contrast 排除无信息画面，
再在剩下的帧里按 sharpness 取最清晰的一帧。
"""

from PIL import Image, ImageFilter, ImageStat, ImageChops

# 统一缩放后再计算，使不同分辨率素材的分数可比，同时大幅降低大图计算量
SHARP_SIZE = (512, 288)   # 清晰度评估尺寸
DIFF_SIZE = (64, 36)      # 帧间差异评估尺寸


def _gray(path, size):
    """读图转灰度并缩放。失败抛出，由调用方决定如何处理。"""
    with Image.open(path) as im:
        return im.convert("L").resize(size)


def sharpness(path):
    """Laplacian 方差。运动模糊 / 黑场 / 纯色画面会得到很低的值。"""
    im = _gray(path, SHARP_SIZE)
    laplacian = im.filter(
        ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1, offset=128)
    )
    return ImageStat.Stat(laplacian).stddev[0] ** 2


def analyze_series(items):
    """对一批有序帧计算 sharpness 与相对前一帧的 diff。

    items: [(timestamp_seconds, Path)]，需按时间升序。
    返回: [{"timestamp_seconds","file","sharpness","contrast","diff"}]
    每帧只解码一次（开一次图同时算清晰度、对比度与差异）。
    """
    out = []
    prev_thumb = None
    for ts, path in items:
        try:
            im = _gray(path, SHARP_SIZE)
            sh = ImageStat.Stat(
                im.filter(
                    ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1, offset=128)
                )
            ).stddev[0] ** 2
            contrast = ImageStat.Stat(im).stddev[0]
            thumb = im.resize(DIFF_SIZE)
            if prev_thumb is None:
                diff = 0.0
            else:
                diff = ImageStat.Stat(ImageChops.difference(thumb, prev_thumb)).mean[0]
            prev_thumb = thumb
        except Exception:
            # 坏帧不参与评估，用极小值占位，后续会被阈值自然排除
            sh, contrast, diff = 0.0, 0.0, 0.0
        out.append({
            "timestamp_seconds": round(float(ts), 3),
            "file": path.name,
            "sharpness": round(sh, 1),
            "contrast": round(contrast, 1),
            "diff": round(diff, 2),
        })
    return out
