# Casos de teste — TDE2

Três arquivos, três formatos. Troque o `test_file` no `task.py` para apontar para cada um.

A numeração dos blocos usada aqui é **sequencial na ordem do arquivo** (`0, 1, 2, …`). Isso importa: alguns blocos não têm label (o `goto` que vem logo depois de um `if`, por exemplo), então numerar pelo label deixaria buracos. Se você preferir numerar pelo label, os blocos sem label vão precisar de um id inventado — escolha uma política e documente.

---

## 1. `c3e.txt` — formato `<bb N>:` (principal)

```
<bb 2>:
i = 0
<bb 3>:
limit=10
<bb 4>:
if i < limit goto bb6
goto bb7;
<bb 6>:
t = a+b
i = i + 1
goto bb4
<bb 7>:
x = t
```

### Blocos esperados

| Bloco | Label | Comandos | Última instrução | Sucessores |
|---|---|---|---|---|
| 0 | `<bb 2>` | `i = 0` | `i = 0` | 1 |
| 1 | `<bb 3>` | `limit=10` | `limit=10` | 2 |
| 2 | `<bb 4>` | `if i < limit goto bb6` | o próprio `if` | 4, 3 |
| 3 | — (sem label) | `goto bb7;` | `goto bb7` | 5 |
| 4 | `<bb 6>` | `t = a+b`, `i = i + 1`, `goto bb4` | `goto bb4` | 2 |
| 5 | `<bb 7>` | `x = t` | `x = t` | — |

### Saída esperada

```
Bloco 0: succs { 1 }
Bloco 1: succs { 2 }
Bloco 2: succs { 4 3 }
Bloco 3: succs { 5 }
Bloco 4: succs { 2 }
Bloco 5: succs { }
```

### O que este arquivo testa

- **Label sem desvio antes** (`<bb 3>:` e `<bb 4>:` vêm depois de atribuições) — a regra 2 dos líderes precisa existir de verdade.
- **Bloco sem label** (bloco 3): o `goto bb7` é líder porque vem logo depois do `if`. Se você numerar blocos pelo label, este caso quebra.
- **Dois sucessores**: bloco 2 → alvo `bb6` (bloco 4) + fall-through (bloco 3).
- **Aresta de retorno**: bloco 4 → bloco 2, o laço.
- **Atribuição de 1 operando** (`limit=10`, `x = t`) e **de 2 operandos** (`t = a+b`, `i = i + 1`).
- **Espaçamento variado** e **ponto e vírgula** depois do `goto bb7;`.

---

## 2. `c3e_lb.txt` — formato do `gerador_c3e.c`

```
LB000:
	T000 = 0
LB001:
	if T000 < 10 goto LB002
	goto LB003
LB002:
	T001 = T000+1
	T000 = T001
	goto LB001
LB003:
	x = T000
```

### Blocos esperados

| Bloco | Label | Comandos | Última instrução | Sucessores |
|---|---|---|---|---|
| 0 | `LB000` | `T000 = 0` | `T000 = 0` | 1 |
| 1 | `LB001` | `if T000 < 10 goto LB002` | o próprio `if` | 3, 2 |
| 2 | — (sem label) | `goto LB003` | `goto LB003` | 4 |
| 3 | `LB002` | `T001 = T000+1`, `T000 = T001`, `goto LB001` | `goto LB001` | 1 |
| 4 | `LB003` | `x = T000` | `x = T000` | — |

### Saída esperada

```
Bloco 0: succs { 1 }
Bloco 1: succs { 3 2 }
Bloco 2: succs { 4 }
Bloco 3: succs { 1 }
Bloco 4: succs { }
```

### O que este arquivo testa

- Labels `LB000` e temporários `T000` (formato do trabalho anterior).
- **Linhas indentadas com tab** — o parser não pode depender de a instrução começar na coluna 0.
- Espaçamento inconsistente do próprio gerador: `T000 = 0` com espaços, `T001 = T000+1` sem espaço em volta do `+`.
- Desvio condicional seguido de `goto` na linha seguinte (o padrão que o gerador sempre emite).

---

## 3. `c3e_edge.txt` — casos de borda

```
<bb 2>:
x = 1
<bb 3>:
<bb 4>:
if x > 0 goto <bb 6>
goto <bb 5>
<bb 5>:
goto <bb 5>
<bb 6>:
```

### Blocos esperados (política A: cada label é seu próprio bloco)

| Bloco | Label | Comandos | Última instrução | Sucessores |
|---|---|---|---|---|
| 0 | `<bb 2>` | `x = 1` | `x = 1` | 1 |
| 1 | `<bb 3>` | *(vazio)* | — | 2 |
| 2 | `<bb 4>` | `if x > 0 goto <bb 6>` | o próprio `if` | 5, 3 |
| 3 | — (sem label) | `goto <bb 5>` | `goto <bb 5>` | 4 |
| 4 | `<bb 5>` | `goto <bb 5>` | `goto <bb 5>` | 4 (auto-laço) |
| 5 | `<bb 6>` | *(vazio, fim do arquivo)* | — | — |

### Saída esperada

```
Bloco 0: succs { 1 }
Bloco 1: succs { 2 }
Bloco 2: succs { 5 3 }
Bloco 3: succs { 4 }
Bloco 4: succs { 4 }
Bloco 5: succs { }
```

### O que este arquivo testa

- **Labels consecutivos** (`<bb 3>:` seguido de `<bb 4>:`), que produzem um bloco vazio.
- **Bloco vazio no fim do arquivo** (`<bb 6>:` sem instrução): não tem sucessor.
- **Auto-laço** (`goto <bb 5>` dentro do próprio bloco 5): sucessor é ele mesmo.
- **Alvo com colchetes angulares** (`goto <bb 6>`): o regex do alvo precisa aceitar esse formato.
- **Fall-through de bloco vazio**: se você mantém blocos vazios, defina que eles caem no próximo (é a política usada na tabela).

### Política B (alternativa)

Se em vez de criar bloco para cada label você **anexar o label à próxima instrução**, então `<bb 3>:` e `<bb 4>:` apontam para o mesmo bloco, o bloco 1 deixa de existir e a numeração desloca:

```
Bloco 0: <bb 2>  x = 1
Bloco 1: <bb 3>/<bb 4>  if x > 0 goto <bb 6>
Bloco 2: goto <bb 5>
Bloco 3: <bb 5>  goto <bb 5>
Bloco 4: <bb 6>  (vazio)
```

As duas políticas são defensáveis. Escolha uma, coloque no README e teste sempre contra a mesma.

---

## Dicas rápidas

- Comece pelo `c3e.txt`: se ele passar, os outros dois são ajuste de regex, não de algoritmo.
- Para depurar, imprima a lista de líderes antes de montar os blocos. Quase todo erro aparece ali.
- Um resultado suspeito de "bloco a mais" geralmente é o `goto` depois do `if` sendo tratado como parte do bloco anterior.
- Um resultado suspeito de "bloco a menos" geralmente é um label que não foi marcado como líder.
