#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
情感分类模型推理演示
===================
使用训练好的模型进行情感分类推理
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
import numpy as np

# 配置
MODEL_PATH = "./sentiment_model"
MAX_LENGTH = 512

# 情感标签
SENTIMENT_LABELS = {0: "负面", 1: "中性", 2: "正面"}

def load_model():
    """加载训练好的模型"""
    print("加载模型...")
    
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    
    # 加载基础模型
    base_model = AutoModelForSequenceClassification.from_pretrained(
        "Qwen/Qwen2-7B-Instruct",
        num_labels=3,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 加载LoRA权重
    model = PeftModel.from_pretrained(base_model, MODEL_PATH)
    model.eval()
    
    return tokenizer, model

def predict_sentiment(text, model, tokenizer):
    """预测文本情感"""
    # 对文本进行编码
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )
    
    # 进行预测
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][predicted_class].item()
    
    # 获取情感描述
    sentiment = SENTIMENT_LABELS[predicted_class]
    
    return predicted_class, sentiment, confidence

def main():
    """主函数"""
    print("="*50)
    print("情感分类推理演示")
    print("="*50)
    
    try:
        # 加载模型
        tokenizer, model = load_model()
        
        # 测试样例
        test_texts = [
            "这个产品质量很好，我很满意！",
            "服务态度很差，让人很失望。",
            "这个价格合理，功能一般。",
            "体验非常棒，强烈推荐！",
            "这个决定让我很后悔。",
            "环境优美，服务周到。",
            "性价比很低，不推荐购买。",
            "这个方案很有创意，解决了问题。",
            "沟通效率很低，让人烦躁。",
            "结果超出预期，非常满意！"
        ]
        
        print("\n开始推理演示...")
        print("-" * 50)
        
        for i, text in enumerate(test_texts, 1):
            label, sentiment, confidence = predict_sentiment(text, model, tokenizer)
            print(f"{i:2d}. 文本: {text}")
            print(f"    情感: {sentiment} (置信度: {confidence:.3f})")
            print()
        
        # 交互式推理
        print("-" * 50)
        print("交互式推理 (输入 'quit' 退出)")
        print("-" * 50)
        
        while True:
            user_input = input("请输入要分析的文本: ").strip()
            if user_input.lower() == 'quit':
                break
            
            if user_input:
                label, sentiment, confidence = predict_sentiment(user_input, model, tokenizer)
                print(f"情感: {sentiment} (置信度: {confidence:.3f})")
                print()
        
        print("推理演示结束！")
        
    except Exception as e:
        print(f"推理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
