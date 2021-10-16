import multiprocessing
import re
from difflib import SequenceMatcher, ndiff
from pathlib import Path
from typing import Union

from julius4seg.converter import conv2openjtalk
from openjtalk_label_getter import FullContextLabel, OutputType, openjtalk_label_getter
from tqdm import tqdm

mora_list = [
    ["、", "", "pau"],
    ["りょ", "ry", "o"],
    ["りゅ", "ry", "u"],
    ["りゃ", "ry", "a"],
    ["りぇ", "ry", "e"],
    ["みょ", "my", "o"],
    ["みゅ", "my", "u"],
    ["みゃ", "my", "a"],
    ["みぇ", "my", "e"],
    ["ぴょ", "py", "o"],
    ["ぴゅ", "py", "u"],
    ["ぴゃ", "py", "a"],
    ["ぴぇ", "py", "e"],
    ["びょ", "by", "o"],
    ["びゅ", "by", "u"],
    ["びゃ", "by", "a"],
    ["びぇ", "by", "e"],
    ["ひょ", "hy", "o"],
    ["ひゅ", "hy", "u"],
    ["ひゃ", "hy", "a"],
    ["ひぇ", "hy", "e"],
    ["にょ", "ny", "o"],
    ["にゅ", "ny", "u"],
    ["にゃ", "ny", "a"],
    ["にぇ", "ny", "e"],
    ["でょ", "dy", "o"],
    ["でゅ", "dy", "u"],
    ["でゃ", "dy", "a"],
    ["でぇ", "dy", "e"],
    ["てょ", "ty", "o"],
    ["てゅ", "ty", "u"],
    ["てゃ", "ty", "a"],
    ["つぉ", "ts", "o"],
    ["つぇ", "ts", "e"],
    ["つぃ", "ts", "i"],
    ["つぁ", "ts", "a"],
    ["つ", "ts", "u"],
    ["ちょ", "ch", "o"],
    ["ちゅ", "ch", "u"],
    ["ちゃ", "ch", "a"],
    ["ちぇ", "ch", "e"],
    ["ち", "ch", "i"],
    ["しょ", "sh", "o"],
    ["しゅ", "sh", "u"],
    ["しゃ", "sh", "a"],
    ["しぇ", "sh", "e"],
    ["し", "sh", "i"],
    ["ぐゎ", "gw", "a"],
    ["くゎ", "kw", "a"],
    ["ぎょ", "gy", "o"],
    ["ぎゅ", "gy", "u"],
    ["ぎゃ", "gy", "a"],
    ["ぎぇ", "gy", "e"],
    ["きょ", "ky", "o"],
    ["きゅ", "ky", "u"],
    ["きゃ", "ky", "a"],
    ["きぇ", "ky", "e"],
    ["う゛ぉ", "v", "o"],
    ["う゛ぇ", "v", "e"],
    ["う゛ぃ", "v", "i"],
    ["う゛ぁ", "v", "a"],
    ["う゛", "v", "u"],
    ["ん", "", "N"],
    ["わ", "w", "a"],
    ["ろ", "r", "o"],
    ["れ", "r", "e"],
    ["る", "r", "u"],
    ["り", "r", "i"],
    ["ら", "r", "a"],
    ["よ", "y", "o"],
    ["ゆ", "y", "u"],
    ["や", "y", "a"],
    ["も", "m", "o"],
    ["め", "m", "e"],
    ["む", "m", "u"],
    ["み", "m", "i"],
    ["ま", "m", "a"],
    ["ぽ", "p", "o"],
    ["ぼ", "b", "o"],
    ["ほ", "h", "o"],
    ["ぺ", "p", "e"],
    ["べ", "b", "e"],
    ["へ", "h", "e"],
    ["ぷ", "p", "u"],
    ["ぶ", "b", "u"],
    ["ふぉ", "f", "o"],
    ["ふぇ", "f", "e"],
    ["ふぃ", "f", "i"],
    ["ふぁ", "f", "a"],
    ["ふ", "f", "u"],
    ["ぴ", "p", "i"],
    ["び", "b", "i"],
    ["ひ", "h", "i"],
    ["ぱ", "p", "a"],
    ["ば", "b", "a"],
    ["は", "h", "a"],
    ["の", "n", "o"],
    ["ね", "n", "e"],
    ["ぬ", "n", "u"],
    ["に", "n", "i"],
    ["な", "n", "a"],
    ["どぅ", "d", "u"],
    ["ど", "d", "o"],
    ["とぅ", "t", "u"],
    ["と", "t", "o"],
    ["でぃ", "d", "i"],
    ["で", "d", "e"],
    ["てぃ", "t", "i"],
    ["て", "t", "e"],
    ["っ", "", "cl"],
    ["だ", "d", "a"],
    ["た", "t", "a"],
    ["ぞ", "z", "o"],
    ["そ", "s", "o"],
    ["ぜ", "z", "e"],
    ["せ", "s", "e"],
    ["ずぃ", "z", "i"],
    ["ず", "z", "u"],
    ["すぃ", "s", "i"],
    ["す", "s", "u"],
    ["じょ", "j", "o"],
    ["じゅ", "j", "u"],
    ["じゃ", "j", "a"],
    ["じぇ", "j", "e"],
    ["じ", "j", "i"],
    ["ざ", "z", "a"],
    ["さ", "s", "a"],
    ["ご", "g", "o"],
    ["こ", "k", "o"],
    ["げ", "g", "e"],
    ["け", "k", "e"],
    ["ぐ", "g", "u"],
    ["く", "k", "u"],
    ["ぎ", "g", "i"],
    ["き", "k", "i"],
    ["が", "g", "a"],
    ["か", "k", "a"],
    ["うぉ", "w", "o"],
    ["うぇ", "w", "e"],
    ["うぃ", "w", "i"],
    ["いぇ", "y", "e"],
    ["お", "", "o"],
    ["え", "", "e"],
    ["う", "", "u"],
    ["い", "", "i"],
    ["あ", "", "a"],
]

mora2yomi = {consonant + vowel: text for [text, consonant, vowel] in mora_list}
yomi2mora = {text: (consonant, vowel) for [text, consonant, vowel] in mora_list}

vowel_list = ("a", "i", "u", "e", "o", "A", "I", "U", "E", "O")
pause_list = ("pau", "sil")
other_list = ("cl", "N")
moraend_list = vowel_list + pause_list + other_list


def decide(jul_phones: list[str], ojt_labels: list[FullContextLabel], verbose=False):
    ojt_phones = [l.phoneme for l in ojt_labels]

    labels: list[Union[FullContextLabel, str]] = []  # FullContextLabelが無かった場合は音素だけが入る
    for tag, s1, e1, s2, e2 in SequenceMatcher(
        None, jul_phones, ojt_phones
    ).get_opcodes():
        if tag == "equal":
            labels += ojt_labels[s2:e2]
            continue

        # print(tag, jul_phones[s1:e1], ojt_phones[s2:e2])

        i1, i2 = s1, s2
        while i1 < e1 or i2 < e2:
            p1 = jul_phones[i1] if i1 < len(jul_phones) else None
            p2 = ojt_phones[i2] if i2 < len(ojt_phones) else None
            l2 = ojt_labels[i2] if i2 < len(ojt_labels) else None

            pp1 = jul_phones[i1 - 1 : i1 + 1] if i1 > 0 else None
            pp2 = ojt_phones[i2 - 1 : i2 + 1] if i2 > 0 else None

            np1 = jul_phones[i1 : i1 + 2] if i1 < len(jul_phones) - 1 else None
            np2 = ojt_phones[i2 : i2 + 2] if i2 < len(ojt_phones) - 1 else None

            inc1 = inc2 = 1

            if i1 == e1:
                inc1 = 0
                inc2 = e2 - i2

            elif p1 == p2:
                labels += [l2]

            elif p2 == "pau":
                inc1 = 0

            elif (p1 == "i" and p2 == "I") or (p1 == "u" and p2 == "U"):
                labels += [l2]

            elif (pp1 == ("o", "u") and pp2 == ("o", "o")) or (
                pp1 == ("e", "i") and pp2 == ("e", "e")
            ):
                labels += [l2]

            elif np1 == ("j", "i") and np2 == ("d", "i"):
                labels += [l2]

            elif np1 == ("j", "u") and np2 == ("d", "u"):
                labels += [l2]

            elif np1 == ("ch", "i") and np2 == ("t", "i"):
                labels += [l2]

            else:
                labels += list(jul_phones[i1:e1])
                inc1 = e1 - i1
                inc2 = e2 - i2

                if verbose:
                    print(list(ndiff(jul_phones[i1:], ojt_phones[i2:])))

            i1 += inc1
            i2 += inc2

    return labels


def alignment(args: tuple[str, str], verbose=False):
    text, yomi = args

    yomi = (
        yomi.replace("？", "、")
        .replace("。", "、")
        .replace("、、", "、")
        .strip("、")
        .replace("、", " sp ")
    )

    jul_phones = conv2openjtalk(yomi).replace("q", "cl").replace("sp", "pau").split()
    ojt_labels = [
        label.label
        for label in openjtalk_label_getter(
            text, output_type=OutputType.full_context_label
        )[1:-1]
    ]

    labels = decide(jul_phones=jul_phones, ojt_labels=ojt_labels, verbose=verbose)
    # breakpoint()
    assert len(labels) == len(jul_phones), args

    if verbose:
        print(" ".join(map(label_to_phone, labels)))
        # print("\n".join([str(label) for label in labels]))
        print("------------------------")

    return ["sil"] + labels + ["sil"]


def label_to_phone(label: Union[FullContextLabel, str]):
    if isinstance(label, str):
        return label
    return label.phoneme


# アクセント情報が書かれた読みを返す
def make_memo(labels: list[Union[FullContextLabel, str]]):
    memo = ""

    for label in labels:
        phone = label_to_phone(label)

        if phone in pause_list:
            memo += "|" + phone + "|"
            continue

        if phone in ["A", "I", "U", "E", "O"]:
            phone = phone.lower()

        if not isinstance(label, FullContextLabel):
            memo += phone + "?"
            continue

        a1, a2, a3 = (
            label.contexts["a1"],
            label.contexts["a2"],
            label.contexts["a3"],
        )

        # if a2 == "1":
        #     memo += "|"

        memo += phone

        if a1 == "0" and phone in moraend_list:
            memo += "'"

        if a3 == "1" and phone in moraend_list:
            memo += "|"

    memo = re.sub(r"\|+", "|", memo)
    memo = re.sub(r"^\|", "", memo)
    memo = re.sub(r"\|$", "", memo)

    old_memo = memo
    memos = []
    for m in old_memo.split("|"):
        if "?" in m:
            m = m.replace("?", "")
            m += "?"
        memos += [m]
    memo = "|".join(memos)

    for mora, yomi in mora2yomi.items():
        memo = memo.replace(mora, yomi)

    # print(memo)
    return memo


def main():
    basic_path = Path("basic5000.txt")
    output_phoneme_path = Path("basic5000_phoneme_openjtalk.txt")
    output_memo_path = Path("basic5000_memo_openjtalk.txt")

    basic_string = basic_path.read_text()

    texts: list[str] = re.findall(r"text_level0\: (.+)", basic_string)
    assert len(texts) == 5000

    yomis: list[str] = re.findall(r"kana_level0\: (.+)", basic_string)
    assert len(yomis) == 5000

    # texts = texts[:20]
    # yomis = yomis[:20]
    # labels_list = [
    #     alignment((text, yomi), verbose=True) for text, yomi in zip(texts, yomis)
    # ]

    with multiprocessing.Pool(processes=16) as pool:
        it = pool.imap(alignment, zip(texts, yomis), chunksize=8)
        labels_list = list(tqdm(it, total=len(texts)))

    output_phoneme_path.write_text(
        "\n".join(" ".join(map(label_to_phone, labels)) for labels in labels_list)
    )

    memo = ""
    for text, labels in zip(texts, labels_list):
        memo += text + "\n"
        memo += make_memo(labels[1:-1]) + "\n"
        memo += "\n"
    output_memo_path.write_text(memo)


if __name__ == "__main__":
    main()
