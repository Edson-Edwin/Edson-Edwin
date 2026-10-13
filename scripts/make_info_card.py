"""Generate the neofetch panel using details from the existing README."""

from pathlib import Path
from svg_utils import start, static, text

ROOT = Path(__file__).resolve().parents[1]


def main():
    svg = start(490, 420, "Edson Edwin Ninan — developer profile", "edson@github: ~")
    rows = [
        ("$ neofetch", "accent", 13),
        ("Edson Edwin Ninan", "bright", 20),
        ("----------------------------", "muted", 12),
        ("Role     Software Developer", "bright", 12),
        ("Focus    Backend & Cloud-Native Systems", "bright", 12),
        ("Stack    Java / Spring Boot / Python", "bright", 12),
        ("Cloud    AWS / Docker / Terraform", "bright", 12),
        ("Data     PostgreSQL / MySQL / MongoDB", "bright", 12),
        ("Study    MCA · Amal Jyothi College", "bright", 12),
        ("         of Engineering · CGPA 8.86", "muted", 12),
        ("Prev     Cloud & DevOps intern @ IPSR", "bright", 12),
        ("Build    REST APIs / Microservices / CI/CD", "bright", 12),
        ("Open to  Software & Backend Engineer roles", "accent", 12),
    ]
    positions = [66, 100, 122, 151, 174, 197, 220, 243, 266, 286, 311, 334, 370]
    for i, ((value, cls, size), y) in enumerate(zip(rows, positions)):
        effect = '' if static() else f' class="reveal" style="animation-delay:{.15+i*.10:.2f}s"'
        svg.append(f'<g{effect}>{text(22, y, value, cls, size)}</g>')
    for i, color in enumerate(["#7ee787", "#58a6ff", "#d2a8ff", "#ffa657", "#ff7b72", "#e6edf3"]):
        svg.append(f'<rect x="{22+i*22}" y="390" width="17" height="8" rx="2" fill="{color}"/>')
    svg.append('</svg>')
    (ROOT / "info-card.svg").write_text("\n".join(svg) + "\n")
    print("Wrote info-card.svg")


if __name__ == "__main__":
    main()
