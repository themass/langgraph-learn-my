#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
情感分类模型训练Demo
===================
使用千问模型进行情感分类任务训练
"""

import os
import torch
import numpy as np
from typing import Dict, List, Tuple
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
class Config:
    model_name = "Qwen/Qwen2-7B-Instruct"
    max_length = 512
    num_labels = 3  # 负面、中性、正面
    batch_size = 4
    learning_rate = 2e-4
    num_epochs = 3
    output_dir = "./sentiment_model"

# 情感标签
SENTIMENT_LABELS = {0: "负面", 1: "中性", 2: "正面"}

def create_synthetic_data():
    """创建合成情感分类数据"""
    negative_texts = [
        "这个产品质量太差了，完全不值这个价格。",
        "服务态度恶劣，让人非常失望。",
        "体验感很差，不会再购买了。",
        "这个决定让我很后悔，浪费了很多时间。",
        "环境很糟糕，噪音很大，无法忍受。"
    ]
    
    neutral_texts = [
        "这个产品功能一般，价格适中。",
        "服务还可以，基本满足需求。",
        "体验一般，没有特别的感觉。",
        "这个决定中规中矩，可以接受。",
        "环境一般，没有特别的亮点。"
    ]
    
    positive_texts = [
        "这个产品质量很好，超出预期。",
        "服务态度优秀，让人很满意。",
        "体验很棒，值得推荐。",
        "这个决定很明智，带来了很多好处。",
        "环境优美，让人心情愉悦。"
    ]
    
    # 生成数据
    data = []
    for text in negative_texts * 20:
        data.append({"text": text, "label": 0})
    for text in neutral_texts * 20:
        data.append({"text": text, "label": 1})
    for text in positive_texts * 20:
        data.append({"text": text, "label": 2})
    
    np.random.shuffle(data)
    
    # 划分数据集
    train_data = data[:80]
    eval_data = data[80:90]
    test_data = data[90:]
    
    return (
        Dataset.from_list(train_data),
        Dataset.from_list(eval_data),
        Dataset.from_list(test_data)
    )

def setup_model_and_tokenizer():
    """设置模型和分词器"""
    logger.info(f"加载模型: {Config.model_name}")
    
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(
        Config.model_name,
        trust_remote_code=True
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 加载模型
    model = AutoModelForSequenceClassification.from_pretrained(
        Config.model_name,
        num_labels=Config.num_labels,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 配置LoRA
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        inference_mode=False,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    
    # 应用LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    return tokenizer, model

def preprocess_function(examples, tokenizer):
    """数据预处理"""
    result = tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=Config.max_length,
        return_tensors="pt"
    )
    result["labels"] = torch.tensor(examples["label"], dtype=torch.long)
    return result

def compute_metrics(pred):
    """计算评估指标"""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    
    accuracy = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted'
    )
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def main():
    """主函数"""
    print("="*50)
    print("情感分类模型训练Demo")
    print("="*50)
    
    try:
        # 1. 加载数据
        logger.info("步骤1: 加载数据集...")
        train_dataset, eval_dataset, test_dataset = create_synthetic_data()
        
        # 2. 设置模型和分词器
        logger.info("步骤2: 设置模型和分词器...")
        tokenizer, model = setup_model_and_tokenizer()
        
        # 3. 数据预处理
        logger.info("步骤3: 数据预处理...")
        train_dataset = train_dataset.map(
            lambda x: preprocess_function(x, tokenizer),
            batched=True
        )
        eval_dataset = eval_dataset.map(
            lambda x: preprocess_function(x, tokenizer),
            batched=True
        )
        
        # 4. 训练模型
        logger.info("步骤4: 训练模型...")
        training_args = TrainingArguments(
            output_dir=Config.output_dir,
            learning_rate=Config.learning_rate,
            per_device_train_batch_size=Config.batch_size,
            per_device_eval_batch_size=Config.batch_size,
            num_train_epochs=Config.num_epochs,
            evaluation_strategy="steps",
            save_strategy="steps",
            eval_steps=50,
            save_steps=50,
            logging_steps=10,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            fp16=True,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )
        
        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
        )
        
        trainer.train()
        trainer.save_model()
        tokenizer.save_pretrained(Config.output_dir)
        
        print(f"\n模型已保存到: {Config.output_dir}")
        print("训练完成！")
        
    except Exception as e:
        logger.error(f"训练过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
