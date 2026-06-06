from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import Agent


def generate_agent_report(viewer: Agent, agents: list[Agent]) -> str:
    lines = [
        f"# MemoryTown AI 최종 리포트 - {viewer.name} 시점",
        "",
        f"- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Agent: {viewer.name} / {viewer.age}세 / {viewer.job}",
        f"- 성격: {viewer.personality}",
        "",
        "## 상대방별 Memory & Relation Map",
        "",
    ]
    others = [agent for agent in agents if agent.name != viewer.name]
    if not others:
        lines.append("다른 Agent가 없어 리포트를 생성할 수 없습니다.")
        return "\n".join(lines)

    for target in others:
        lines.extend([f"### {target.name}", "", "#### 1) 알고 있는 사실"])
        facts = viewer.known_facts_about(target.name)
        if facts:
            for item in facts:
                context = []
                if item.day:
                    context.append(f"{item.day}일차")
                if item.time_slot:
                    context.append(item.time_slot)
                context_label = f" ({', '.join(context)})" if context else ""
                lines.append(f"- [Round {item.round_id}]{context_label} {item.fact}")
        else:
            lines.append("- 아직 저장된 사실이 없습니다.")
        lines.extend(["", "#### 2) 관계 요약 / Reflection"])
        lines.append(viewer.relation_summary_for(target.name))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def save_agent_report(markdown: str, report_dir: str | Path, agent_name: str) -> Path:
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(ch for ch in agent_name if ch.isalnum() or ch in ("_", "-")) or "agent"
    path = directory / f"{safe_name}_final_report.md"
    path.write_text(markdown, encoding="utf-8")
    return path
