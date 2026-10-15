"""Transposição dos exercícios para os 12 tons.

Tudo aqui roda em cima da teoria pura (theory.py), sem precisar do LilyPond:
o grau e o desvio de acidente de cada nota (em relação à escala MAIOR da
tônica original) são calculados uma vez e reaplicados sobre a escala maior
da tônica alvo. Isso funciona igual para maior, menor natural/harmônica/
melódica — e até para exercícios que misturam duas escalas no mesmo
compasso (ex7_3, ex8_3), porque o desvio é calculado nota a nota, não
escolhido por exercício inteiro.

Gera, para cada exercício de ex.py, os dados dos 12 tons (notas para a
pauta em formato VexFlow + áudio já transposto) que viram partituras/
transpose_data.js em montar.py.
"""
import re
from fractions import Fraction

from theory import Note, NAT, LETTERS, parse, scale

# tabela cromática fixa (convenção: bemóis, exceto o trítono em sustenido —
# assim nenhuma das 12 escalas maiores precisa de acidente duplo)
PC_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
# no modo menor, "Réb menor" pediria uma armadura de Fáb maior (impossível de
# escrever/o VexFlow rejeita) — usa o enarmônico "Dó# menor" só nesse grau
PC_NAMES_MENOR = list(PC_NAMES)
PC_NAMES_MENOR[1] = "C#"
PC_PT = {
    "C": "Dó", "Db": "Réb", "D": "Ré", "Eb": "Mib", "E": "Mi", "F": "Fá",
    "F#": "Fá#", "G": "Sol", "Ab": "Láb", "A": "Lá", "Bb": "Sib", "B": "Si",
    "C#": "Dó#",
}

# tônica original (letra + acidente, sem oitava) e modo de cada exercício —
# levantado lendo ex.py (qual field()/scale_score()/chord_from() deu origem
# a cada partitura).
ORIGIN = {
    "ex1_1": ("C", "maior"), "ex1_2": ("C", "maior"), "ans1_2": ("C", "maior"),
    "ex2_1": ("C", "maior"), "ex2_2": ("C", "maior"), "ex2_3": ("C", "maior"),
    "ex2_4g": ("G", "maior"), "ex2_4f": ("F", "maior"), "ex2_4d": ("D", "maior"),
    "ex2_5": ("G", "maior"), "ans2_5": ("G", "maior"), "ex2_6": ("C", "maior"),
    "ex3_1": ("C", "maior"), "ex3_2": ("C", "maior"), "ex3_3": ("C", "maior"),
    "ex4_1": ("C", "maior"), "ex4_2": ("C", "maior"), "ex4_3": ("C", "maior"),
    "ex4_4": ("G", "maior"), "ex4_5": ("F", "maior"),
    "ex4_6": ("D", "maior"), "ans4_6": ("D", "maior"),
    "ex4_7": ("Bb", "maior"), "ans4_7": ("Bb", "maior"),
    "ex5_1": ("C", "maior"), "ex5_2": ("G", "maior"), "ex5_3": ("C", "maior"),
    "ex5_4": ("C", "maior"), "ex5_5": ("C", "maior"),
    "ex6_1": ("A", "menor"), "ex6_2": ("A", "menor"), "ex6_3": ("A", "menor"),
    "ex6_4": ("E", "menor"), "ex6_5": ("D", "menor"), "ex6_6": ("A", "menor"),
    "ex7_1": ("A", "menor"), "ex7_2": ("A", "menor"), "ex7_3": ("A", "menor"),
    "ex7_4": ("A", "menor"), "ex7_5": ("D", "menor"),
    "ex8_1": ("A", "menor"), "ex8_2": ("A", "menor"), "ex8_3": ("A", "menor"),
    "ex8_4": ("A", "menor"),
}

CIFRA_RE = re.compile(r"^([A-G])([#b]{0,2})(.*)$")

# exercícios em que o parâmetro "grau" guarda o nome da nota em português
# (ex1_1: "Dó","Ré","Mi"...), não o grau da escala ("1","b3"...) — esse sim
# precisa transpor junto com a nota, ao contrário do grau normal (que é
# relativo à tônica e não muda de tom).
GRAU_E_NOME_DE_NOTA = {"ex1_1"}


def _tonic_note(t):
    return parse(t) if isinstance(t, str) else t


def transpose_note(note, from_tonic, to_tonic):
    """Transpõe uma Note (qualquer oitava) de from_tonic para to_tonic,
    preservando grau e qualidade do intervalo (b3, #4, bb7...), com
    respeito a registro (desloca pelo caminho mais curto de semitons)."""
    t1, t2 = _tonic_note(from_tonic), _tonic_note(to_tonic)
    maj1, maj2 = scale(t1, "maior"), scale(t2, "maior")
    d = (note.l - t1.l) % 7
    diff = note.acc - maj1[d].acc
    shift = ((t2.pc - t1.pc + 6) % 12) - 6
    new_midi = note.midi + shift
    l2 = (t2.l + d) % 7
    acc2 = maj2[d].acc + diff
    if acc2 > 2 or acc2 < -2:
        # fora do que dá para escrever (bb..##): respelha com a letra vizinha
        l2 = (l2 + (1 if acc2 < 0 else -1)) % 7
        acc2 = (new_midi % 12) - NAT[l2]
        if acc2 > 6:
            acc2 -= 12
        elif acc2 < -6:
            acc2 += 12
    oct2 = (new_midi - NAT[l2] - acc2) // 12 - 1
    return Note(l2, acc2, oct2)


def transpose_label(text, from_tonic, to_tonic):
    """Transpõe só a raiz de uma cifra ("Dm7" -> "Em7") ou nome de nota solto
    ("C" -> "D"). Números de grau ("1","b3") e romanos ("IIm7") não mudam —
    já são relativos à tônica — e "_" (caixa em branco de quiz) fica "_"."""
    if text is None or text == "_":
        return text
    m = CIFRA_RE.match(text)
    if not m:
        return text
    letter, accs, rest = m.groups()
    acc = accs.count("#") - accs.count("b")
    root = transpose_note(Note(letter, acc, 4), from_tonic, to_tonic)
    return root.name() + rest


# fração -> (código de duração do VexFlow, pontuado?)
DUR_VF = {
    Fraction(1): ("w", False), Fraction(1, 2): ("h", False), Fraction(1, 4): ("q", False),
    Fraction(1, 8): ("8", False), Fraction(1, 16): ("16", False),
    Fraction(3, 4): ("h", True), Fraction(3, 8): ("q", True), Fraction(3, 16): ("8", True),
    Fraction(3, 2): ("w", True),
}


def vf_key(note):
    acc = {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}[note.acc]
    return f"{LETTERS[note.l].lower()}{acc}/{note.oct}"


def key_spec(tonic, mode):
    return tonic + ("m" if mode == "menor" else "")


def export_score(score, name):
    """Monta, para os 12 tons, a lista de eventos (pauta) + áudio já
    transposto de um Score (ex.py). Não depende do LilyPond."""
    from montar import pad_midis  # import tardio: evita ciclo no nível de módulo

    origin, mode = ORIGIN[name]
    names_list = PC_NAMES if mode == "maior" else PC_NAMES_MENOR
    keys_out = []
    for pc in names_list:
        is_original = pc == origin
        events = []
        audio_n, audio_p = [], []
        t = Fraction(0)
        cur = None
        for kind, note, d, roman, cifra, grau, color in score.ev:
            dl, dots = DUR_VF[d]
            ev = {"t": kind, "dur": dl, "beats": float(d * 4)}
            if dots:
                ev["dots"] = 1
            if color:
                # score.ev só usa COL_HI (lyb.py) como destaque — aqui já em CSS, não na
                # sintaxe scheme do LilyPond ("#(rgb-color ...)")
                ev["color"] = "#B0362A"
            if roman is not None:
                ev["roman"] = roman
            if cifra is not None:
                ev["cifra"] = transpose_label(cifra, origin, pc)
            midi = 0
            tn = None
            if kind == "n":
                tn = transpose_note(note, origin, pc)
                ev["key"] = vf_key(tn)
                midi = tn.midi
            if grau is not None:
                ev["grau"] = tn.pt() if (tn and name in GRAU_E_NOME_DE_NOTA) else grau
            events.append(ev)

            if score.pad and cifra and cifra != "_":
                ms = pad_midis(transpose_label(cifra, origin, pc), score.triads)
                if ms:
                    if cur:
                        audio_p.append([float(cur[0] * 4), cur[1], float((t - cur[0]) * 4)])
                    cur = (t, ms)
            audio_n.append([midi, float(d * 4)])
            t += d
        if cur:
            audio_p.append([float(cur[0] * 4), cur[1], float((t - cur[0]) * 4)])

        keys_out.append({
            "tonic": pc,
            "label": PC_PT[pc] + (" maior" if mode == "maior" else " menor") + (" (original)" if is_original else ""),
            "isOriginal": is_original,
            "keySpec": key_spec(pc, mode),
            "events": events,
            "play": {"n": audio_n, "p": audio_p},
        })

    return {
        "mode": mode,
        "originalTonic": origin,
        "time": score.time,
        "beatsPerMeasure": int(score.time.split("/")[0]),
        "breaks": sorted(score.breaks),
        "mobileBreaks": sorted(score.mobile_breaks),
        "keys": keys_out,
    }


def export_all(EX):
    return {name: export_score(s, name) for name, s in EX.items() if name in ORIGIN}
