#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

import numpy as np
import time
import torch
import tqdm
import json

from slowfast.utils import logging
from slowfast.visualization.async_predictor import AsyncDemo, AsyncVis
from slowfast.visualization.ava_demo_precomputed_boxes import AVAVisualizerWithPrecomputedBox
from slowfast.visualization.demo_loader import ThreadVideoManager, VideoManager
from slowfast.visualization.predictor import ActionPredictor
from slowfast.visualization.video_visualizer import VideoVisualizer

logger = logging.get_logger(__name__)


def run_demo(cfg, frame_provider):
    """
    Генерирует задачи (task) с результатами инференса модели.
    Каждая задача возвращается для дальнейшей обработки/отображения/сохранения.
    """
    np.random.seed(cfg.RNG_SEED)
    torch.manual_seed(cfg.RNG_SEED)
    logging.setup_logging(cfg.OUTPUT_DIR)

    logger.info("Run demo with config:")
    logger.info(cfg)

    common_classes = (
        cfg.DEMO.COMMON_CLASS_NAMES
        if len(cfg.DEMO.LABEL_FILE_PATH) != 0
        else None
    )

    video_vis = VideoVisualizer(
        num_classes=cfg.MODEL.NUM_CLASSES,
        class_names_path=cfg.DEMO.LABEL_FILE_PATH,
        top_k=cfg.TENSORBOARD.MODEL_VIS.TOPK_PREDS,
        thres=cfg.DEMO.COMMON_CLASS_THRES,
        lower_thres=cfg.DEMO.UNCOMMON_CLASS_THRES,
        common_class_names=common_classes,
        colormap=cfg.TENSORBOARD.MODEL_VIS.COLORMAP,
        mode=cfg.DEMO.VIS_MODE,
    )

    async_vis = AsyncVis(video_vis, n_workers=cfg.DEMO.NUM_VIS_INSTANCES)

    # Выбираем модель (один GPU) или асинхронную (несколько GPU).
    if cfg.NUM_GPUS <= 1:
        model = ActionPredictor(cfg=cfg, async_vis=async_vis)
    else:
        model = AsyncDemo(cfg=cfg, async_vis=async_vis)

    seq_len = cfg.DATA.NUM_FRAMES * cfg.DATA.SAMPLING_RATE
    # Проверяем, что размер буфера разумен.
    assert (
        cfg.DEMO.BUFFER_SIZE <= seq_len // 2
    ), "Buffer size cannot be greater than half of sequence length."

    num_task = 0
    frame_provider.start()

    # Считываем задачи (task) из frame_provider, передаём их модели, возвращаем результат.
    for able_to_read, task in frame_provider:
        if not able_to_read:
            break
        if task is None:
            time.sleep(0.02)
            continue
        num_task += 1
        model.put(task)
        try:
            task = model.get()  # Забираем готовый task с инференсом
            num_task -= 1
            yield task
        except IndexError:
            continue

    # Дожидаемся, пока все задачи будут обработаны.
    while num_task != 0:
        try:
            task = model.get()
            num_task -= 1
            yield task
        except IndexError:
            continue


def demo(cfg):
    """
    Запускает инференс на входном видео:
    1) Отображает/сохраняет результат (через frame_provider.display).
    2) Собирает данные (frame_idx, preds) из task и записывает их в JSON.
    """
    if cfg.DETECTION.ENABLE and cfg.DEMO.PREDS_BOXES != "":
        # Случай AVA: предобработанные боксы.
        precomputed_box_vis = AVAVisualizerWithPrecomputedBox(cfg)
        precomputed_box_vis()
    else:
        start = time.time()
        if cfg.DEMO.THREAD_ENABLE:
            frame_provider = ThreadVideoManager(cfg)
        else:
            frame_provider = VideoManager(cfg)

        results = []

        # Запускаем инференс, получаем task'и из run_demo
        for task in tqdm.tqdm(run_demo(cfg, frame_provider)):
            # 1) Отображаем/сохраняем в видео.
            frame_provider.display(task)

            # 2) Сохраняем данные о кадрах/предсказаниях в список.
            # Предполагаем, что task.frame_idx и task.preds заполнены в predictor.py
            # Превращаем task в dict через __dict__.
            task_dict = task.__dict__

            # Извлекаем атрибуты (если они есть).
            frame_idx = task_dict.get("frame_idx", None)
            preds = task_dict.get("preds", None)

            # Если preds — тензор, приводим к списку.
            if isinstance(preds, torch.Tensor):
                preds = preds.cpu().tolist()

            # Можно добавлять и другие поля (meta, bboxes, action_preds и т.д.)
            results.append({
                "frame_idx": frame_idx,
                "preds": preds,
            })

        # Останавливаем чтение/запись.
        frame_provider.join()
        frame_provider.clean()

        # Сохраняем результаты в JSON.
        output_path = "demo_results.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=4)

        logger.info(
            f"Results saved to {output_path}. "
            f"Finish demo in: {time.time() - start:.2f} s"
        )


if __name__ == "__main__":
    from slowfast.config.defaults import get_cfg
    cfg = get_cfg()

    # Здесь можно задать:
    # cfg.DEMO.INPUT_VIDEO = "/mnt/c/qw1/Animal_Kingdom/action_recognition/your_video.mp4"
    # cfg.DEMO.OUTPUT_FILE = "./logs/slowfast/demo_output.mp4"
    # И другие нужные параметры.

    demo(cfg)
