from typing import Dict, List, Optional, Tuple, Union

import wandb

import numpy as np

from ultralytics.yolo.engine.results import Results
from ultralytics.yolo.v8.classify.predict import ClassificationPredictor


def plot_classification_predictions(
    result: Results, table: Optional[wandb.Table] = None
):
    result = result.to("cpu")
    probabilities = result.probs
    probabilities_list = probabilities.data.numpy().tolist()
    class_id_to_label = {int(k): str(v) for k, v in result.names.items()}
    table_row = [
        wandb.Image(result.orig_img[:, :, ::-1]),
        class_id_to_label[int(probabilities.top1)],
        probabilities.top1conf,
        [class_id_to_label[int(class_idx)] for class_idx in list(probabilities.top5)],
        [probabilities_list[int(class_idx)] for class_idx in list(probabilities.top5)],
        {
            class_id_to_label[int(class_idx)]: probability
            for class_idx, probability in enumerate(probabilities_list)
        },
        result.speed,
    ]
    if table is not None:
        table.add_data(*table_row)
        return table
    return table_row


def plot_classification_validation_results(
    dataloader,
    predictor: ClassificationPredictor,
    table: wandb.Table,
    max_validation_batches: int,
    epoch: Optional[int] = None,
):
    data_idx = 0
    for batch_idx, batch in enumerate(dataloader):
        image_batch = batch["img"].numpy()
        for img_idx in range(image_batch.shape[0]):
            image = np.ascontiguousarray(np.transpose(image_batch[img_idx], (1, 2, 0)))
            prediction_result = predictor(image)[0]
            table_row = plot_classification_predictions(prediction_result)
            table_row = [data_idx, batch_idx] + table_row
            table_row = [epoch] + table_row if epoch is not None else table_row
            table.add_data(*table_row)
            data_idx += 1
        if batch_idx + 1 == max_validation_batches:
            break
    return table
