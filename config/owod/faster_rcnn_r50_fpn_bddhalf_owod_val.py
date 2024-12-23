_base_ = [
    "../_base_/models/faster_rcnn_r50_fpn.py",
    "../_base_/runtimes/default_runtime.py",
    "../_base_/schedules/default_schedule.py",
]

CLASSES = ("pedestrian", "bicycle", "car", "traffic sign", "unknown")

custom_imports = dict(
    imports=[
        "safednn_naptron.uncertainty.owod.roi_head",
        "safednn_naptron.uncertainty.owod.bbox_head",
        "safednn_naptron.uncertainty.owod.random_sampler",
        "safednn_naptron.uncertainty.coco_ood_dataset",
    ],
    allow_failed_imports=False,
)

score_thr = 0.01

model = dict(
    roi_head=dict(
        type="OWODRoiHead",
        num_classes=5,
        clustering_items_per_class=4,
        clustering_start_iter=2000,
        clustering_update_mu_iter=3000,
        clustering_momentum=0.99,
        enable_clustering=False,
        prev_intro_cls=0,
        curr_intro_cls=4,
        max_iterations=60000,
        output_dir="work_dirs/owod_bdd",
        feat_store_path="feature_store",
        margin=10,
        compute_energy=True,
        energy_save_path="work_dirs/owod_bdd/energy",
        bbox_head=dict(type="OWODBBoxHead", num_classes=5),
    ),
    train_cfg=dict(
        rcnn=dict(
            sampler=dict(
                type="OWODSampler",
            ),
        )
    ),
    test_cfg=dict(rcnn=dict(score_thr=score_thr)),
)


temperature = 1.5

dataset_type = "CocoDataset"
data_root = "data/bdd100k/"

img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True
)
train_pipeline = [
    dict(type="LoadImageFromFile"),
    dict(type="LoadAnnotations", with_bbox=True),
    dict(type="Resize", img_scale=(1000, 600), keep_ratio=True),
    dict(type="RandomFlip", flip_ratio=0.5),
    dict(type="Normalize", **img_norm_cfg),
    dict(type="Pad", size_divisor=32),
    dict(type="DefaultFormatBundle"),
    dict(type="Collect", keys=["img", "gt_bboxes", "gt_labels"]),
]
test_pipeline = [
    dict(type="LoadImageFromFile"),
    dict(
        type="MultiScaleFlipAug",
        img_scale=(1000, 600),
        flip=False,
        transforms=[
            dict(type="Resize", keep_ratio=True),
            dict(type="RandomFlip"),
            dict(type="Normalize", **img_norm_cfg),
            dict(type="Pad", size_divisor=32),
            dict(type="ImageToTensor", keys=["img"]),
            dict(type="Collect", keys=["img"]),
        ],
    ),
]
data = dict(
    samples_per_gpu=4,
    workers_per_gpu=8,
    train=dict(
        type="RepeatDataset",
        times=3,
        dataset=dict(
            type=dataset_type,
            ann_file=data_root + "labels/det_val_coco.json",
            img_prefix=data_root + "images/100k/val",
            pipeline=train_pipeline,
            classes=CLASSES,
        ),
    ),
    val=dict(
        type=dataset_type,
        ann_file=data_root + "labels/det_val_coco.json",
        img_prefix=data_root + "images/100k/val",
        pipeline=train_pipeline,
        classes=CLASSES,
    ),
    test=dict(
        type=dataset_type,
        ann_file=data_root + "labels/det_val_coco.json",
        img_prefix=data_root + "images/100k/val",
        pipeline=train_pipeline,
        classes=CLASSES,
    ),
)
evaluation = dict(interval=1, metric="bbox")

# optimizer
optimizer = dict(type="SGD", lr=0.01, momentum=0.9, weight_decay=0.0001)
# runtime settings
runner = dict(type="EpochBasedRunner", max_epochs=1)

load_from = "work_dirs/faster_rcnn_r50_fpn_bddhalf_owod/latest.pth"
