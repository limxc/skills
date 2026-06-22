#!/usr/bin/env python3
"""Analyze OpenSpec change material and extract content categories for diagram type recommendation.

Usage:
    python scripts/analyze_change_material.py <change-dir>

Outputs JSON with content categories derived from proposal.md and design.md.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


def score_content(text: str) -> dict[str, float]:
    categories = {
        "architecture": [
            # English
            r"\barchitect", r"\bcomponent", r"\bmodule", r"\bservice",
            r"\blayer", r"\bmicroservice", r"\bdeploy", r"\bcontainer",
            r"\bcluster", r"\bgateway", r"\bproxy", r"\bmiddleware",
            r"\binfrastructure", r"\btopology",
            # Chinese
            r"架构", r"组件", r"模块", r"服务[^.]{,10}(?:层|拆分|新增)",
            r"层[次级]", r"微服务", r"部署", r"容器", r"集群",
            r"网关", r"代理", r"中间件", r"基础设施", r"拓扑",
        ],
        "api": [
            # English
            r"\bapi", r"\bendpoint", r"\broute", r"\bgraphql", r"\brest",
            r"\brequest", r"\bresponse", r"\bhttp", r"\bwebsocket",
            r"\bgrpc", r"\bprotobuf", r"\binterface", r"\brpc",
            r"\bmessage", r"\bpayload",
            # Chinese
            r"接口", r"端点", r"路由", r"请求", r"响应",
            r"通讯", r"协议", r"消息[^.]{,5}(?:传递|队列)",
        ],
        "data_model": [
            # English
            r"\bentity", r"\bmodel", r"\bschema", r"\btable",
            r"\bfield", r"\bcolumn", r"\brelation", r"\bdatabase",
            r"\bforeign key", r"\bprimary key", r"\bindex",
            r"\bmigration", r"\btype\b", r"\bstruct", r"\battribute",
            # Chinese
            r"数据模型", r"实体", r"模型[^.]{,10}(?:类|字段|数据)",
            r"模式", r"表[^.]{,5}(?:结构|字段)",
            r"字段", r"列", r"关系", r"数据库", r"外键", r"主键",
            r"索引", r"迁移", r"属性",
        ],
        "workflow": [
            # English
            r"\bworkflow", r"\bpipeline", r"\bprocess", r"\bflow",
            r"\bstep", r"\bstage", r"\bphase", r"\borchestrat",
            r"\bchain", r"\bsequence", r"\border", r"\bexecution",
            r"\bci/cd",
            # Chinese
            r"工作流", r"流程", r"管道", r"步骤", r"阶段",
            r"编排", r"顺序", r"执行[^.]{,10}(?:链|流程)", r"构建",
        ],
        "state": [
            # English
            r"\bstate", r"\bstatus", r"\blifecycle", r"\btransition",
            r"\bfsm", r"\bstate machine", r"\bphase",
            r"\binitializ", r"\bterminat", r"\bfinite",
            # Chinese
            r"状态[^.]{,5}(?:机|转换|流转)", r"生命周期",
            r"转换", r"初始化", r"终止",
        ],
        "timeline": [
            # English
            r"\bmilestone", r"\btimeline", r"\bschedule", r"\bphase",
            r"\bdeadline", r"\bversion", r"\brelease", r"\broadmap",
            r"\biteration", r"\bsprint",
            # Chinese
            r"里程碑", r"时间线", r"日程", r"截止日期",
            r"版本", r"发布", r"路线图", r"迭代",
        ],
    }

    text_lower = text.lower()
    scores = {}
    for category, patterns in categories.items():
        count = sum(len(re.findall(p, text_lower)) for p in patterns)
        scores[category] = round(count / max(len(text_lower), 100), 3)
    return scores


def extract_entities(text: str) -> list[str]:
    entities = re.findall(r'[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)+', text)
    single_words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    word_counts = Counter(single_words)
    entities.extend(w for w, c in word_counts.items() if c >= 3 and w not in entities)
    return list(dict.fromkeys(entities))[:15]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_change_material.py <change-dir>", file=sys.stderr)
        return 1

    change_dir = Path(sys.argv[1])
    if not change_dir.is_dir():
        print(f"Error: change directory not found: {change_dir}", file=sys.stderr)
        return 1

    texts = {}
    for fname in ["proposal.md", "design.md"]:
        fpath = change_dir / fname
        if fpath.is_file():
            texts[fname] = fpath.read_text(encoding="utf-8")
        else:
            texts[fname] = ""

    combined = " ".join(texts.values())
    if not combined.strip():
        print(f"Error: No proposal.md or design.md found in {change_dir}", file=sys.stderr)
        return 1

    scores = score_content(combined)
    entities = extract_entities(combined)

    threshold = 0.05
    categories = {
        name: score
        for name, score in sorted(scores.items(), key=lambda x: -x[1])
        if score >= threshold
    }
    primary = [name for name, score in categories.items() if score >= 0.12]

    summary = ""
    if texts.get("proposal.md"):
        lines = texts["proposal.md"].splitlines()
        summary_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped and len(stripped) > 20:
                summary_lines.append(stripped)
            if len(summary_lines) >= 3:
                break
        summary = " ".join(summary_lines)[:500]

    result = {
        "change_name": change_dir.name,
        "categories": categories,
        "primary_categories": primary,
        "key_entities": entities[:10],
        "summary": summary,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
