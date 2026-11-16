"""
Rules to be a basic block:

1. O controle entra apenas no primeiro statement do bloco.
2. O controle sai apenas do último statement do bloco.
3. Não há nenhum statement dentro do bloco que possa ser alcançado de fora do bloco, exceto pelo primeiro statement.

Lideres

1. O primeiro statement do programa é um líder.
2. Qualquer statement que seja o alvo de um salto condicional ou incondicional é um líder.
3. Qualquer statement que siga imediatamente um salto condicional ou incondicional é um líder.

Formação de blocos básicos

1. Cada líder inicia um novo bloco básico.
2. Os statements entre dois líderes formam um bloco básico.
3. labels não são incluídos em blocos básicos, mas são associados ao bloco básico que eles precedem.

"""

import re

test_file = "c3e.txt"
output_file = "saida.txt"

with open(test_file, "r") as f:
    lines = []

    while True:
        line = f.readline()

        if not line:
            break

        if not line.strip():
            continue

        if re.search(r"^\s*if\s+.*\s+goto\s+(<bb\s*(\d+)>|[A-Za-z_]\w*)", line):
            m = re.search(r"^\s*if\s+.*\s+goto\s+(<bb\s*(\d+)>|[A-Za-z_]\w*)", line)
            target = f"bb{m.group(2)}" if m.group(2) else m.group(1)
            lines.append(
                {
                    "line": line.strip(),
                    "type": "conditional_goto",
                    "target": target,
                }
            )

        elif re.search(r"^\s*goto\s+(<bb\s*(\d+)>|[A-Za-z_]\w*)", line):
            m = re.search(r"^\s*goto\s+(<bb\s*(\d+)>|[A-Za-z_]\w*)", line)
            target = f"bb{m.group(2)}" if m.group(2) else m.group(1)
            lines.append(
                {
                    "line": line.strip(),
                    "type": "goto",
                    "target": target,
                }
            )

        elif re.search(r"^\s*(?:<bb\s*(\d+)>\s*:?|([A-Za-z_]\w*)\s*:)\s*$", line):
            m = re.search(r"^\s*(?:<bb\s*(\d+)>\s*:?|([A-Za-z_]\w*)\s*:)\s*$", line)
            name = f"bb{m.group(1)}" if m.group(1) else m.group(2)
            lines.append(
                {
                    "line": line.strip(),
                    "type": "label",
                    "name": name,
                    "tag": name,
                }
            )
        elif re.search(r"^\s*\w+\s*=\s*\w+\s*$", line) or re.search(
            r"^\s*\w+\s*=\s*\w+\s*[\+\-\*\/]\s*\w+\s*$", line
        ):
            lines.append(
                {
                    "line": line.strip(),
                    "type": "assignment",
                }
            )
        else:
            lines.append(
                {
                    "line": line.strip(),
                    "type": "other",
                }
            )

    leaders = [False for i in range(len(lines))]
    if lines:
        leaders[0] = True

    for i, ins in enumerate(lines):
        if ins["type"] == "label":
            leaders[i] = True

        if ins["type"] in ("goto", "conditional_goto") and i + 1 < len(lines):
            leaders[i + 1] = True

    basic_blocks = []
    bb_counter = 0
    label_to_block = {}

    for i, ins in enumerate(lines):
        if leaders[i]:
            basic_blocks.append({"id": bb_counter, "instructions": []})
            bb_counter += 1

        basic_blocks[-1]["instructions"].append(ins)

        if ins["type"] == "label":
            label_to_block[ins["name"]] = basic_blocks[-1]["id"]

    for b, bb in enumerate(basic_blocks):
        last = None
        for ins in reversed(bb["instructions"]):
            if ins["type"] != "label":
                last = ins
                break

        succs = []

        if last is None:
            if b + 1 < len(basic_blocks):
                succs.append(b + 1)
        elif last["type"] == "goto":
            if last["target"] not in label_to_block:
                print(f"Erro: desvio para label inexistente '{last['target']}'")
                raise SystemExit(1)
            succs.append(label_to_block[last["target"]])
        elif last["type"] == "conditional_goto":
            if last["target"] not in label_to_block:
                print(f"Erro: desvio para label inexistente '{last['target']}'")
                raise SystemExit(1)
            succs.append(label_to_block[last["target"]])
            if b + 1 < len(basic_blocks) and b + 1 not in succs:
                succs.append(b + 1)
        else:
            if b + 1 < len(basic_blocks):
                succs.append(b + 1)

        bb["succs"] = succs

    output = []

    for bb in basic_blocks:
        succs = " ".join(str(s) for s in bb["succs"])
        if succs:
            output.append(f"Basic Block {bb['id']}: succs {{ {succs} }}")
        else:
            output.append(f"Basic Block {bb['id']}: succs {{ }}")

        for ins in bb["instructions"]:
            output.append(f"  {ins['line']}")
        output.append("")

    text = "\n".join(output)

    with open(output_file, "w") as f:
        f.write(text)

    print(text)
