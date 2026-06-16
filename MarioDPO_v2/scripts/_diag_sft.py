"""Diagnostic: mirror 03_sft.py steps with flushed prints to find the crash."""
import sys


def p(msg):
    print(f"[diag] {msg}", flush=True)
    sys.stdout.flush()


p("start")
import _bootstrap  # noqa
p("bootstrap ok")

from mariodpo_v2.config import load_config
from mariodpo_v2.constants import PROJECT_DIR
p("constants/config import ok")

from mariodpo_v2.modeling import (
    build_sft_texts, count_tile_chars_covered, load_model,
    load_tokenizer, resolve_fp16, tokenize_texts,
)
p("modeling import ok")

from mariodpo_v2.tracking import LocalLogger, resolve_report_to, setup_wandb_env
from mariodpo_v2.utils import load_dotenv, set_seed, setup_logging
p("tracking/utils import ok")

load_dotenv()
p("dotenv ok")
cfg = load_config(PROJECT_DIR / "configs/sft.yaml", [])
p(f"config ok: base={cfg['base_model']}")
set_seed(42)
p("seed ok")
setup_wandb_env()
p("wandb env ok")

from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
p("transformers Trainer import ok")

tokenizer = load_tokenizer(cfg["base_model"])
p(f"tokenizer ok: len={len(tokenizer)}")
covered = count_tile_chars_covered(tokenizer)
p(f"tiles covered: {covered}/37")

texts = build_sft_texts(win_cols=int(cfg.get("win_cols", 50)),
                        stride=cfg.get("stride"),
                        upweight_original=int(cfg.get("upweight_original", 3)),
                        limit_per_generator=cfg.get("limit_per_generator"))
p(f"sft texts: {len(texts)}")

dataset = tokenize_texts(texts, tokenizer, max_length=int(cfg.get("max_length", 256)))
p(f"dataset tokenized: {len(dataset)}")

model = load_model(cfg["base_model"])
p("model loaded")
model.resize_token_embeddings(len(tokenizer))
p("resized embeddings")

import torch
p(f"cuda available: {torch.cuda.is_available()}")
model = model.cuda()
p("model moved to cuda")

fp16 = resolve_fp16(cfg.get("fp16", False))
p(f"fp16={fp16}")

targs = TrainingArguments(
    output_dir=str(PROJECT_DIR / "models/sft_diag"),
    overwrite_output_dir=True,
    max_steps=3,
    per_device_train_batch_size=int(cfg.get("per_device_train_batch_size", 8)),
    gradient_accumulation_steps=int(cfg.get("gradient_accumulation_steps", 4)),
    learning_rate=float(cfg.get("learning_rate", 5e-5)),
    logging_steps=1,
    save_steps=1000,
    fp16=fp16,
    report_to=[],  # disable wandb for this diag
    seed=42,
)
p("TrainingArguments ok")

collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)
trainer = Trainer(model=model, args=targs, train_dataset=dataset, data_collator=collator)
p("Trainer constructed")
result = trainer.train()
p(f"train done: {result.metrics}")
p("ALL OK")
