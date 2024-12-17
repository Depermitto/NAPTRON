_base_ = [
    "../_base_/models/retinanet_r50_fpn.py",
    "../bdd/bdd100k_cocofmt_half.py",
    "../_base_/runtimes/default_runtime.py",
    "../_base_/schedules/default_schedule.py",
]

custom_imports = dict(
    imports=[
        "safednn_naptron.uncertainty.naptron.retina_head",
        "safednn_naptron.uncertainty.naptron.retinanet",
        "safednn_naptron.uncertainty.coco_ood_dataset",
    ],
    allow_failed_imports=False,
)

output_handler = dict(type="simple_dump")

score_thr = 0.01

model = dict(
    type="NAPTRONRetinaNet",
    bbox_head=dict(
        type="NAPTRONRetinaHead",
        num_classes=4,
    ),
    test_cfg=dict(score_thr=score_thr),
)

# optimizer
optimizer = dict(type="SGD", lr=0.01, momentum=0.9, weight_decay=0.0001)
