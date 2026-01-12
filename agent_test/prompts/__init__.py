#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Prompt 模板配置模块
所有推理范式的 prompt 模板都在这里定义
"""

from .cot_prompts import (
    COT_SYSTEM_PROMPT,
    format_analyze_prompt,
    format_reasoning_prompt,
    format_conclude_prompt
)

from .react_prompts import (
    REACT_SYSTEM_PROMPT,
    format_think_prompt,
    format_finish_prompt
)

from .tot_prompts import (
    TOT_SYSTEM_PROMPT,
    format_generate_prompt,
    format_evaluate_prompt,
    format_expand_prompt
)

from .self_consistency_prompts import (
    SELF_CONSISTENCY_SYSTEM_PROMPT,
    format_generate_prompt as format_sc_generate_prompt,
    format_evaluate_prompt as format_sc_evaluate_prompt
)

from .self_reflection_prompts import (
    SELF_REFLECTION_SYSTEM_PROMPT,
    format_generate_prompt as format_sr_generate_prompt,
    format_reflect_prompt,
    format_improve_prompt
)

__all__ = [
    # CoT
    'COT_SYSTEM_PROMPT',
    'format_analyze_prompt',
    'format_reasoning_prompt',
    'format_conclude_prompt',
    # ReAct
    'REACT_SYSTEM_PROMPT',
    'format_think_prompt',
    'format_finish_prompt',
    # ToT
    'TOT_SYSTEM_PROMPT',
    'format_generate_prompt',
    'format_evaluate_prompt',
    'format_expand_prompt',
    # Self-Consistency
    'SELF_CONSISTENCY_SYSTEM_PROMPT',
    'format_sc_generate_prompt',
    'format_sc_evaluate_prompt',
    # Self-Reflection
    'SELF_REFLECTION_SYSTEM_PROMPT',
    'format_sr_generate_prompt',
    'format_reflect_prompt',
    'format_improve_prompt',
]
