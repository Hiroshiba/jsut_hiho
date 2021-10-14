import multiprocessing
import re
from difflib import SequenceMatcher, ndiff
from pathlib import Path

from julius4seg.converter import conv2openjtalk
from openjtalk_label_getter import openjtalk_label_getter
from tqdm import tqdm


def decide_phone(jul_phones: list[str], ojt_phones: list[str], verbose=False):
    phones: list[str] = []
    for tag, s1, e1, s2, e2 in SequenceMatcher(
        None, jul_phones, ojt_phones
    ).get_opcodes():
        if tag == "equal":
            phones += ojt_phones[s2:e2]
            continue

        # print(tag, jul_phones[s1:e1], ojt_phones[s2:e2])

        i1, i2 = s1, s2
        while i1 < e1 or i2 < e2:
            p1 = jul_phones[i1] if i1 < len(jul_phones) else None
            p2 = ojt_phones[i2] if i2 < len(ojt_phones) else None

            pp1 = jul_phones[i1 - 1 : i1 + 1] if i1 > 0 else None
            pp2 = ojt_phones[i2 - 1 : i2 + 1] if i2 > 0 else None

            np1 = jul_phones[i1 : i1 + 2] if i1 < len(jul_phones) - 1 else None
            np2 = ojt_phones[i2 : i2 + 2] if i2 < len(ojt_phones) - 1 else None

            nnp1 = jul_phones[i1 : i1 + 3] if i1 < len(jul_phones) - 2 else None
            nnp2 = ojt_phones[i2 : i2 + 3] if i2 < len(ojt_phones) - 2 else None

            inc1 = inc2 = 1

            if i1 == e1:
                inc1 = 0
                inc2 = e2 - i2

            elif p1 == p2:
                phones += [p2]

            elif p2 == "pau":
                inc1 = 0

            elif (p1 == "i" and p2 == "I") or (p1 == "u" and p2 == "U"):
                phones += [p2]

            elif (pp1 == ("o", "u") and pp2 == ("o", "o")) or (
                pp1 == ("e", "i") and pp2 == ("e", "e")
            ):
                phones += [p2]

            elif np1 == ("h", "a") and np2 == ("w", "a"):
                raise Exception()

            elif np1 == ("h", "e") and p2 == "e":
                raise Exception()

            elif np1 == ("j", "i") and np2 == ("d", "i"):
                phones += [p2]

            elif np1 == ("j", "u") and np2 == ("d", "u"):
                phones += [p2]

            elif np1 == ("ch", "i") and np2 == ("t", "i"):
                phones += [p2]

            elif np1 == ("i", "u") and nnp2 == ("y", "u", "u"):
                phones += list(np2)
                inc2 = 2

            elif nnp1 == ("y", "u", "u") and np2 == ("i", "u"):
                phones += list(np1)
                inc1 = 2

            else:
                phones += list(jul_phones[i1:e1])
                inc1 = e1 - i1
                inc2 = e2 - i2

                if verbose:
                    print(list(ndiff(jul_phones[i1:], ojt_phones[i2:])))

            i1 += inc1
            i2 += inc2

    return phones


def process(args: tuple[str, str], verbose=False):
    text, yomi = args

    yomi = (
        yomi.replace("？", "、")
        .replace("。", "、")
        .replace("、、", "、")
        .strip("、")
        .replace("、", " sp ")
    )

    jul_phones = conv2openjtalk(yomi).replace("q", "cl").replace("sp", "pau").split()
    ojt_phones = [label.label for label in openjtalk_label_getter(text)[1:-1]]

    phones = decide_phone(jul_phones=jul_phones, ojt_phones=ojt_phones, verbose=verbose)
    # breakpoint()
    assert len(phones) == len(jul_phones), args

    if verbose:
        print(phones)
        print("------------------------")

    return ["sil"] + phones + ["sil"]


def to_phoneme():
    basic_path = Path("basic5000.txt")
    output_path = Path("basic5000_phoneme_openjtalk.txt")

    basic_string = basic_path.read_text()

    texts: list[str] = re.findall(r"text_level0\: (.+)", basic_string)
    assert len(texts) == 5000

    yomis: list[str] = re.findall(r"kana_level0\: (.+)", basic_string)
    assert len(yomis) == 5000

    # phonemes_list = [
    #     process((text, yomi), verbose=True) for text, yomi in zip(texts, yomis)
    # ]

    with multiprocessing.Pool(processes=16) as pool:
        it = pool.imap(process, zip(texts, yomis), chunksize=8)
        phonemes_list = list(tqdm(it, total=len(texts)))

    output_path.write_text("\n".join(" ".join(phonemes) for phonemes in phonemes_list))


if __name__ == "__main__":
    to_phoneme()
