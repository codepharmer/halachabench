import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from halachabench.io_utils import read_jsonl
from halachabench.schema import compute_question_id, validate_questions


RELEASE_DATE = "2026-02-06"
LICENSE = "CC-BY 4.0"
ATTRIBUTION = "HalachaBench (benchmark question set; user-provided)"


def minutes_after_midnight(hh: int, mm: int) -> int:
    return hh * 60 + mm


def render_prompt(
    *,
    assumptions: str | None,
    stem: str,
    options: list[str] | None,
    instructions: str,
) -> str:
    parts: list[str] = []
    if assumptions:
        parts.append(assumptions.strip())
        parts.append("")

    parts.append(stem.strip())

    if options:
        parts.append("")
        for letter, option in zip(["A", "B", "C", "D"], options):
            parts.append(f"{letter}. {option}")

    parts.append("")
    parts.append(instructions.strip())
    return "\n".join(parts).strip()


def make_question(
    *,
    category: str,
    task: str,
    prompt: str,
    answer_type: str,
    ground_truth: Any,
    acceptable_answers: list[Any] | None = None,
    tolerance: float | None = None,
    tolerance_type: str | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "category": category,
        "task": task,
        "turns": [{"role": "user", "content": prompt.strip()}],
        "answer_type": answer_type,
        "ground_truth": ground_truth,
        "release_date": RELEASE_DATE,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
    }
    if acceptable_answers is not None:
        q["acceptable_answers"] = acceptable_answers
    if tolerance is not None:
        q["tolerance"] = tolerance
    if tolerance_type is not None:
        q["tolerance_type"] = tolerance_type
    q["question_id"] = compute_question_id(q)
    return q


def build_questions() -> list[dict[str, Any]]:
    cat1 = "Daily Halacha Core"
    cat2 = "Lifecycle and Real-World Practice"
    cat3 = "Learning and Literacy"
    cat4 = "Hashkafa"
    cat5 = "Chassidus / Machshava / Mussar"
    cat6 = "Jewish Life Operations"

    c1_assumptions = "\n".join(
        [
            "Global assumptions for this category:",
            "- Mainstream Ashkenazi / Mishnah Berurah-style practice.",
            "- No eruv unless stated.",
            "- Shiur chart: kezayis = 27 mL; revi'is = 86 mL; k'dei achilas pras = 4 minutes.",
            "- Meat->milk waiting: 6 hours from the last bite of meat.",
            "- Yad soledes bo = 43C / 110F.",
        ]
    )

    c2_assumptions = "\n".join(
        [
            "Global assumptions for this category:",
            "- Ashkenazi-oriented baseline.",
            "- Where real life has many sub-cases, use the simplified benchmark rule stated in the question.",
        ]
    )

    hashkafa_lens = "\n".join(
        [
            "Lens definitions used for this benchmark:",
            "- Rambam-style rationalist lens: avoids physical descriptions of Hashem; emphasizes careful, non-anthropomorphic language.",
            "- Maharal-style metaphysical lens: emphasizes inner essence/pnimiyus and symbolic/spiritual structure behind mitzvos and reality.",
        ]
    )

    specs: list[dict[str, Any]] = []

    # Populated in chunks below.
    # Category 1 - Daily Halacha Core (1/2)
    specs += [
        {
            "category": cat1,
            "task": "shabbos_carrying_malbush_tachshit",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c1_assumptions,
            "stem": (
                "Shabbos (Carrying / MCQ): You are outside in a place with no eruv. "
                "Which item is permitted to take out because it is considered a normal garment/jewelry "
                "(malbush/tachshit) rather than carrying?"
            ),
            "options": [
                "House key on a lanyard around your neck",
                "Wallet in your jacket pocket",
                "Plain wedding ring worn normally on your finger",
                "A small siddur carried in your back pocket",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "shabbos_muktzeh_ltzorech_gufo_mekomo",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Shabbos (Muktzeh / MCQ): A hammer is on the table (assume: kli shemelachto l'issur). "
                "Which use is the clearest case of moving it permitted (l'tzorech gufo or l'tzorech mekomo)?"
            ),
            "options": [
                "To put it away neatly so the room looks nicer",
                "To use it to crack walnuts for immediate eating",
                "To move it because you don't like seeing it",
                "To move it from one shelf to another \"just in case\"",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "shabbos_timers_policy",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": c1_assumptions,
            "stem": (
                "Shabbos (Timers / MCQ): Policy for this benchmark: you may set timers before Shabbos only "
                "for things whose automatic operation is not doing a forbidden melacha in your framework. "
                "Which is permitted?"
            ),
            "options": [
                "Set a timer before Shabbos to turn a lamp on at 8:00 PM",
                "Set a timer before Shabbos to start an oven baking at 9:00 PM",
                "Set a timer before Shabbos to start a washing machine at midnight",
                "Set a timer before Shabbos to start a hair dryer at 6:30 AM",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "shabbos_hot_water_source",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c1_assumptions,
            "stem": (
                "Shabbos (Hot water / MCQ): You want hot water for tea on Shabbos. "
                "Which source is permitted under these benchmark assumptions?"
            ),
            "options": [
                "An electric urn that will re-activate heating when water level drops",
                "A kettle sitting on a blech, still at/above yad soledes",
                "Water poured into a thermos before Shabbos, still hot now",
                "An \"instant-hot\" dispenser that heats on demand when you press the lever",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "shabbos_blech_chazarah_conditions",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": c1_assumptions,
            "stem": (
                "Shabbos (Blech / chazarah / MCQ): You removed a pot of fully-cooked cholent from a blech "
                "to serve. Under this benchmark's chazarah policy, which set of conditions is the one "
                "that matters most for permitting return to the blech?"
            ),
            "options": [
                "Fully cooked + still warm + you intended to return it + it never left your hand/was still being held",
                "Fully cooked + you intended to return it, even if it cooled completely",
                "Not fully cooked + still warm + you intended to return it",
                "Fully cooked + no intention to return, but you changed your mind",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "shabbos_open_packaging_destructive",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Shabbos (Opening packages / MCQ): Benchmark policy: You may open food packaging on Shabbos "
                "if you do it in a destructive way, and you don't create a neat, durable opening meant "
                "for repeated use. Which opening method fits best?"
            ),
            "options": [
                "Carefully cut a straight \"zipper-like\" opening so the bag can be re-closed neatly",
                "Rip open the top of a snack bag in a messy tear and discard the torn strip",
                "Cut a perfect rectangular \"pour spout\" into a cereal box top",
                "Punch a clean round hole in a plastic lid specifically to create a reusable spout",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "brachos_ikar_tafel_cornflakes_milk",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Brachos (Ikar/tafel / MCQ): You eat a bowl of cornflakes with milk, and most bites include "
                "both. What is the correct beracha rishona on the bowl?"
            ),
            "options": [
                "Shehakol",
                "Borei minei mezonos",
                "Ha'adamah",
                "Two berachos: mezonos on flakes and shehakol on milk",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "brachos_mixed_foods_fruit_salad",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": c1_assumptions,
            "stem": (
                "Brachos (Mixed foods / MCQ): You eat a fruit salad containing mostly apple chunks, with a "
                "small amount of chopped walnuts mixed in mainly to add crunch. What beracha rishona do you "
                "make on the salad?"
            ),
            "options": [
                "Ha'etz only",
                "Ha'adamah only",
                "Shehakol only",
                "Two berachos: ha'etz on apples and ha'etz again on walnuts separately",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "brachos_shinui_makom_cake",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Brachos (Shinui makom / MCQ): You ate cake (mezonos) at your dining table, then went outside "
                "to your backyard without intending to continue eating, and later you decide to eat more "
                "cake outside. Under this benchmark's shinui makom rules, what do you do?"
            ),
            "options": [
                "No new beracha; it's the same food",
                "Make a new mezonos because you changed locations without intent to continue",
                "Only make a new beracha if you left the property",
                "Only make a new beracha if it's a different brand of cake",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "brachos_safek_berachos_water",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Brachos (Safek brachos / MCQ): You are holding a cup of water. You might have already said "
                "shehakol a minute ago, but you're genuinely unsure. What do you do under safek brachos "
                "l'hakel?"
            ),
            "options": [
                "Say shehakol again to be safe",
                "Do not say a beracha; drink without a beracha",
                "Say Baruch Shem Kevod... and then say shehakol",
                "Say borei nefashos first, then drink",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 1 - Daily Halacha Core (2/2)
    specs += [
        {
            "category": cat1,
            "task": "brachos_acharonah_kezayis_cake",
            "answer_type": "enum",
            "answer": "al hamichya",
            "acceptable_answers": ["al hamichya", "al_hamichya", "al ha-michya", "alhamichya"],
            "assumptions": c1_assumptions,
            "stem": (
                "Brachos (Bracha acharona thresholds / Short answer): Using the benchmark shiurim "
                "(kezayis = 27 mL; k'dei achilas pras = 4 minutes): You ate 32 mL of cake within 3 minutes. "
                "What beracha acharona (if any) is required?"
            ),
            "options": None,
            "instructions": "Answer with exactly one of: al hamichya, borei nefashos, or none.",
        },
        {
            "category": cat1,
            "task": "tefillah_zmanim_latest_shema_gra",
            "answer_type": "numeric",
            "answer": minutes_after_midnight(9, 45),
            "tolerance": 0,
            "assumptions": c1_assumptions,
            "stem": (
                "Tefillah (Zmanim algorithm / Short answer): Use this algorithm: Daytime = sunrise to sunset; "
                "Sha'ah zmanis = daytime / 12. Given: sunrise 6:24 AM, sunset 7:48 PM. "
                "What is the latest time for Krias Shema (Gra) = end of 3 sha'os zmaniyos?"
            ),
            "options": None,
            "instructions": "Answer as minutes after midnight (0-1439).",
        },
        {
            "category": cat1,
            "task": "tefillah_tashlumin_mincha_at_maariv",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Tefillah (Tashlumin / MCQ): You missed Mincha entirely (forgot), and now it's at night and "
                "you're about to daven Ma'ariv. What is the correct tashlumin sequence?"
            ),
            "options": [
                "One Ma'ariv Amidah only; no tashlumin exists",
                "Two Amidahs at Ma'ariv: first for Ma'ariv, second as tashlumin for Mincha",
                "Two Amidahs at Ma'ariv: first for Mincha, second for Ma'ariv",
                "Make up Mincha the next day at Shacharis",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "tefillah_amidah_wrong_nusach_weekday",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Tefillah (Amidah mistake / MCQ): On a weekday you accidentally began Shmoneh Esrei and said "
                "\"Ata kidashta...\" (the Shabbos nusach) instead of weekday. You realize your mistake before "
                "finishing the first beracha. What do you do?"
            ),
            "options": [
                "Finish the Shabbos Amidah; it counts b'diavad",
                "Stop immediately and restart the weekday Amidah from the beginning",
                "Continue until you reach \"Retzei,\" then switch",
                "Say \"Baruch Shem...\" and then continue",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "tefillah_yaaleh_veyavo_repeat",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Tefillah (Ya'aleh Veyavo / MCQ): On Rosh Chodesh, you forgot Ya'aleh Veyavo in Shacharis and "
                "only realized after finishing the Amidah (but before taking 3 steps back). What do you do?"
            ),
            "options": [
                "Don't repeat; safek brachos l'hakel",
                "Repeat the Amidah",
                "Say Ya'aleh Veyavo right there without repeating",
                "Only repeat if you also forgot Hallel",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "tefillah_interrupt_pdz_kaddish",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c1_assumptions,
            "stem": (
                "Tefillah (Tzibbur rules / MCQ): You are in the middle of Pesukei d'Zimra and the minyan "
                "begins Kaddish. Under this benchmark's rules, which response is most appropriate?"
            ),
            "options": [
                "Say nothing; you may not interrupt for any Kaddish",
                "Answer only \"Amen\" at the end, not \"Yehei Shmei Rabba\"",
                "Answer \"Yehei Shmei Rabba...\" and the main amens (permitted interruptions)",
                "Stop and say the entire Kaddish with the chazan",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "kashrus_bishul_akum_rema_fire_participation",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c1_assumptions,
            "stem": (
                "Kashrus basics (Bishul akum / MCQ): Benchmark policy: follow the Rema-style requirement that "
                "a Jew's participation in the fire/heat source can qualify food as bishul Yisrael (within "
                "defined bounds). Scenario: A Jew turns on the flame; a non-Jew places a pot of raw vegetables "
                "on the flame and cooks them fully. What is the status?"
            ),
            "options": [
                "Always permitted (bishul akum never applies to vegetables)",
                "Depends: if the food is fit for a king's table and not eaten raw, bishul akum may apply; Jewish fire participation may matter",
                "Always forbidden because only a Jew may place the pot on the fire",
                "Always forbidden unless a Jew stirs continuously",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "kashrus_bittul_bshishim_milk_in_meat",
            "answer_type": "json",
            "answer": {"soup_ml": 240, "milk_ml": 5, "soup_to_milk_ratio": 48, "is_batel_bshishim": False},
            "assumptions": c1_assumptions,
            "stem": (
                "Kashrus basics (Ta'aruvos / ratio / Short answer): Hot meat soup: 240 mL. Cold milk "
                "accidentally splashes in: 5 mL. Assume this is a classic milk-in-meat mixture case where "
                "the relevant question is bitul b'shishim (ignore other complications for this benchmark)."
            ),
            "options": None,
            "instructions": (
                "Return a JSON object with keys: soup_ml (number), milk_ml (number), soup_to_milk_ratio "
                "(number), is_batel_bshishim (true/false)."
            ),
        },
        {
            "category": cat1,
            "task": "kashrus_waiting_6h_from_last_bite",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": c1_assumptions,
            "stem": (
                "Kashrus basics (Waiting time / MCQ): Policy: 6 hours from the last bite of meat. Which case "
                "is permitted to have dairy at 7:00 PM?"
            ),
            # NOTE: Adjusted option A time from 1:30 PM -> 1:00 PM to ensure exactly one correct answer
            # under the stated 6-hours-from-last-bite policy.
            "options": [
                "Last bite of meat at 1:00 PM; finished bentching at 1:45 PM",
                "Last bite of meat at 1:10 PM; chewed meat stuck between teeth until 2:00 PM",
                "Last bite of meat at 2:05 PM; no meat after that",
                "Last bite of meat at 1:20 PM; had chicken soup (with meat) again at 1:50 PM",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat1,
            "task": "kashrus_bliah_ben_yomo_status_first_question",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c1_assumptions,
            "stem": (
                "Kashrus basics (Kli status / MCQ): You accidentally stirred a hot meat pot (yad soledes) with "
                "a clean dairy spoon that had not been used in 24 hours. Benchmark simplification: treat this "
                "as a classic bliah question. What is the first status question you must resolve to determine "
                "next steps?"
            ),
            "options": [
                "Whether the spoon is silver or stainless steel",
                "Whether the pot was on the fire or off the fire",
                "Whether the spoon and pot were ben yomo / not, and the temperature (yad soledes)",
                "Whether the food tastes good",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 2 - Lifecycle and Real-World Practice (1/2)
    specs += [
        {
            "category": cat2,
            "task": "niddah_hefsek_earliest_day_5day_minimum",
            "answer_type": "enum",
            "answer": "Friday",
            "acceptable_answers": ["Friday", "Day 5", "day 5", "Day 5 (Friday)", "Friday (Day 5)"],
            "assumptions": c2_assumptions,
            "stem": (
                "Niddah / Taharas Hamishpacha (Veses/hefsek timing / Short answer): Benchmark rule: minimum "
                "5 days from the start of bleeding before a hefsek taharah (even if bleeding stops earlier). "
                "Bleeding begins Monday afternoon (call that Day 1). It stops Thursday morning. "
                "What is the earliest day she may do a hefsek taharah under this rule?"
            ),
            "options": None,
            "instructions": "Answer with a day name (e.g., Monday, Tuesday, ...).",
        },
        {
            "category": cat2,
            "task": "niddah_hefsek_close_to_sunset_effect",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Niddah / Taharas Hamishpacha (Hefsek close to sunset / MCQ): She performs hefsek taharah at "
                "7 minutes before sunset and it is clean. For this benchmark, assume that counts as done "
                "\"by day.\" What does that affect most?"
            ),
            "options": [
                "Whether she needs bedikot at all",
                "Whether that day can count as the hefsek day starting the seven nekiyim process",
                "Whether she must wait 6 days instead of 5",
                "Whether she may go to mikvah without seven nekiyim",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "niddah_bedikah_missed_day1_benchmark_continue",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Niddah / Taharas Hamishpacha (Bedikah missed / MCQ): Benchmark rule: bedikot are required on "
                "Day 1 and Day 7 of the seven nekiyim. If Day 1 bedikah was missed, but Day 2 was done clean, "
                "you may continue (benchmark simplification). She forgot the first bedikah of the seven "
                "nekiyim but did a clean bedikah on the second day. What happens?"
            ),
            "options": [
                "She must restart the seven nekiyim",
                "She continues the count (under the benchmark rule)",
                "She can skip all remaining bedikot",
                "She goes to mikvah immediately",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "niddah_kesamim_size_color_benchmark",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Niddah / Taharas Hamishpacha (Kesamim rule / MCQ): Benchmark rule for stains: On white "
                "underwear, a stain >= 2 cm diameter is treated as problematic. On colored underwear, ignore "
                "stains < 2 cm. She finds a 1.5 cm stain on colored underwear during seven nekiyim. "
                "What is the benchmark outcome?"
            ),
            "options": [
                "Breaks the count; restart seven nekiyim",
                "Does not break the count",
                "Requires immediate mikvah that night",
                "Requires waiting 24 hours and then restarting",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "niddah_mikvah_night_after_hefsek",
            "answer_type": "enum",
            "answer": "Sunday night",
            "acceptable_answers": ["Sunday night", "Sunday night (after day 7)", "Sunday night after day 7"],
            "assumptions": c2_assumptions,
            "stem": (
                "Niddah / Taharas Hamishpacha (Mikvah night / Short answer): She does a hefsek on Sunday "
                "before sunset and begins counting seven nekiyim. Under the benchmark rule, on which night is "
                "mikvah night (assuming all checks are clean)?"
            ),
            "options": None,
            "instructions": "Answer with a day name + \"night\" (e.g., \"Sunday night\").",
        },
        {
            "category": cat2,
            "task": "niddah_delay_after_7_nekiyim_bedikot_each_day",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c2_assumptions,
            "stem": (
                "Niddah / Taharas Hamishpacha (Delay after seven nekiyim / MCQ): She completed seven nekiyim "
                "and was supposed to go to mikvah Sunday night, but mikvah is closed and she can only go "
                "Tuesday night. Benchmark rule: when delayed, she should do a bedikah each day of delay. "
                "Which is correct?"
            ),
            "options": [
                "No bedikot needed after day 7; just go Tuesday night",
                "One bedikah Tuesday afternoon only",
                "Bedikah Monday + bedikah Tuesday before mikvah",
                "Must restart seven nekiyim due to delay",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "aveilus_shiva_end_day7_miktzas_hayom",
            "answer_type": "enum",
            "answer": "Tuesday morning",
            "acceptable_answers": ["Tuesday morning", "Tuesday (morning)", "Tuesday, morning"],
            "assumptions": c2_assumptions,
            "stem": (
                "Aveilus (Counting shiva / Short answer): The kevurah is on Wednesday at 2:00 PM. Under the "
                "benchmark rule: the day of burial counts as Day 1 of shiva. When does shiva end (which day/"
                "time conceptually)?"
            ),
            "options": None,
            "instructions": "Answer with a day name + \"morning\" (e.g., \"Tuesday morning\").",
        },
        {
            "category": cat2,
            "task": "aveilus_burial_near_sunset_consequence",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": c2_assumptions,
            "stem": (
                "Aveilus (Burial near sunset / MCQ): Kevurah happens on Friday 25 minutes before sunset. "
                "Benchmark rule: that partial day counts as Day 1, and Shabbos counts in shiva. "
                "What is the most direct consequence?"
            ),
            "options": [
                "Shiva ends one calendar day earlier than if burial was after sunset",
                "Shiva does not begin until Sunday",
                "The aveil has no shiva because Shabbos cancels it",
                "Shiva is always exactly 7 full 24-hour periods",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "aveilus_yomtov_cuts_shiva",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Aveilus (Yom Tov interaction / MCQ): Benchmark rule: if a full Yom Tov begins after shiva "
                "started, the public aveilus practices stop and Yom Tov can \"cut off\" shiva. "
                "Which scenario best matches this?"
            ),
            "options": [
                "Death occurs on Yom Tov; burial after Yom Tov",
                "Burial occurs two days before Yom Tov begins",
                "Burial occurs on Shabbos",
                "Yom Tov begins during shloshim",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "aveilus_shmuah_rechokah_after_30_days",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Aveilus (Shmuah rechokah / MCQ): Benchmark rule: hearing about a close relative's death after "
                "30 days is shmuah rechokah with reduced aveilus. He hears about the petirah 35 days after "
                "the burial. What category is this?"
            ),
            "options": ["Shmuah kerovah", "Shmuah rechokah", "Aninus", "Not aveilus at all"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 2 - Lifecycle and Real-World Practice (2/2)
    specs += [
        {
            "category": cat2,
            "task": "aveilus_shloshim_haircut_shaving",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c2_assumptions,
            "stem": (
                "Aveilus (Shloshim restrictions / MCQ): During shloshim (after shiva), which restriction is "
                "most classically still in force (benchmark level)?"
            ),
            "options": [
                "Sitting on low chairs",
                "Not working at all",
                "Avoiding haircuts / shaving (depending on circumstances)",
                "Not wearing leather shoes",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "chagim_chametz_assur_bmashehu",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Chagim (Pesach ta'aruvos / MCQ): Benchmark rule: chametz on Pesach is assur b'mashehu "
                "(ignore unusual edge cases). A crumb of chametz fell into a pot of soup on Pesach. "
                "What's the benchmark result?"
            ),
            "options": [
                "Batel b'shishim, permitted",
                "Assur b'mashehu, forbidden",
                "Permitted if you remove the crumb",
                "Permitted if it was less than a kezayis",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "chagim_kitniyos_identify_non_kitniyos",
            "answer_type": "enum",
            "answer": "D",
            "assumptions": c2_assumptions,
            "stem": (
                "Chagim (Kitniyos track / MCQ): Benchmark: follow common Ashkenazi practice that kitniyos are "
                "not eaten, and kitniyos-derived products are treated as prohibited for this benchmark. "
                "Which food is not kitniyos under this benchmark?"
            ),
            "options": ["Rice", "Lentils", "Corn", "Potatoes"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "chagim_erev_pesach_cutoffs",
            "answer_type": "json",
            "answer": {
                "sof_zman_achilas_chametz_minutes": minutes_after_midnight(10, 42),
                "sof_zman_biur_chametz_minutes": minutes_after_midnight(11, 53),
            },
            "assumptions": c2_assumptions,
            "stem": (
                "Chagim (Erev Pesach timing / Short answer): Given: sof zman achilas chametz = 10:42 AM; "
                "sof zman biur chametz = 11:53 AM. Under this benchmark, by what time must one stop eating "
                "chametz, and by what time must one finish destroying/disposing chametz?"
            ),
            "options": None,
            "instructions": (
                "Return a JSON object with keys: sof_zman_achilas_chametz_minutes (number), "
                "sof_zman_biur_chametz_minutes (number). Values are minutes after midnight."
            ),
        },
        {
            "category": cat2,
            "task": "chagim_bedikas_chametz_missed_next_day_no_bracha",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Chagim (Bedikas chametz missed / MCQ): He forgot to do bedikas chametz on the proper night. "
                "Benchmark rule: if you do bedikah the next day, you do it without the normal nighttime-style "
                "bracha. What do you do?"
            ),
            "options": [
                "Do bedikah the next day with a bracha",
                "Do bedikah the next day without a bracha",
                "Skip bedikah and rely only on bittul",
                "Do bedikah only on Pesach morning",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "chagim_sefiras_haomer_missed_night_counted_daytime",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": c2_assumptions,
            "stem": (
                "Chagim (Sefiras haOmer mistake / MCQ): He forgot to count at night, but remembered and "
                "counted the next day before sunset. What is the benchmark ruling for the next night?"
            ),
            "options": [
                "Continue counting with a bracha",
                "Continue counting without a bracha for the rest of the Omer",
                "Stop counting entirely",
                "Restart from Day 1",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "chagim_sefirah_safek_count_without_bracha",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Chagim (Sefirah safek / MCQ): Benchmark rule: If you are unsure whether you counted last "
                "night, you count now without a bracha, and you may continue future nights with a bracha. "
                "He is unsure at 10:30 PM whether he counted last night. What should he do now?"
            ),
            "options": [
                "Count with a bracha now",
                "Count without a bracha now",
                "Don't count now; wait until tomorrow daytime",
                "Stop counting with a bracha forever",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "tzedakah_maaser_10pct_takehome_after_tax",
            "answer_type": "numeric",
            "answer": 450,
            "tolerance": 0,
            "assumptions": c2_assumptions,
            "stem": (
                "Tzedakah / ribbis basics (Ma'aser / Short answer): Benchmark rule: you separate 10% from "
                "your take-home pay after taxes (benchmark simplification). Monthly gross: $6,000. "
                "Taxes/withholding: $1,500. What is the monthly ma'aser amount under this benchmark?"
            ),
            "options": None,
            "instructions": "Answer as a number (USD).",
        },
        {
            "category": cat2,
            "task": "ribbis_late_fee_time_based_extra",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": c2_assumptions,
            "stem": (
                "Tzedakah / ribbis basics (Ribbis / MCQ): You lend your friend $1,000 for 30 days. The "
                "contract says: \"If you pay after 30 days, you must pay an extra $25 late fee.\" No heter "
                "iska. Benchmark rule: extra money purely due to time is ribbis. What is this?"
            ),
            "options": [
                "Permitted; it's just a penalty, not interest",
                "Ribbis (forbidden) under the benchmark rule",
                "Permitted if both parties agree",
                "Permitted if the borrower is not Jewish",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat2,
            "task": "ribbis_discount_vs_surcharge",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": c2_assumptions,
            "stem": (
                "Tzedakah / ribbis basics (Discount vs surcharge / MCQ): Benchmark rule: A discount for early "
                "payment is generally not ribbis, but a surcharge for late payment is ribbis (when structured "
                "as time-based extra money on a loan). Which is the ribbis problem case?"
            ),
            "options": [
                "\"Pay within 10 days: $95; otherwise $100\" for a purchase",
                "\"List price $100; you may pay $95 today\" for a purchase",
                "\"Borrow $100; repay $100 today or $110 in 30 days\"",
                "\"Donation pledge: suggested amounts vary by tier\"",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 3 - Learning and Literacy (1/2)
    specs += [
        {
            "category": cat3,
            "task": "rashi_bereishis_11_r_yitzchak_purpose",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Rashi's motivation / MCQ): Rashi on Bereishis 1:1 brings "
                "\"אמר רבי יצחק...\" about why the Torah begins with Creation. What \"problem\" is he "
                "addressing?"
            ),
            "options": [
                "A grammatical issue in the word \"Bereishis\"",
                "A justification of Israel's claim to Eretz Yisrael against \"the nations\"",
                "Why Adam was created on Friday",
                "Why there are two creation narratives",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "pshat_vs_derash_ein_tachas_ein",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Pshat vs derash / MCQ): \"עין תחת עין\" - In halachic tradition it "
                "is understood as monetary compensation. In this question, classify that reading as:"
            ),
            "options": [
                "Pure pshat only",
                "Derash/halachic interpretation (Chazal)",
                "A modern metaphorical reading",
                "A textual emendation",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "rashi_vayikach_korach_grammar_gap",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Identify the question Rashi answers / MCQ): Rashi on \"ויקח קרח\" "
                "(Bamidbar 16:1) famously addresses: \"What did Korach 'take'?\" Which type of issue is this?"
            ),
            "options": [
                "A missing object/grammar problem in the pasuk",
                "A contradiction between two psukim far apart",
                "A historical question about Egypt",
                "A numerical inconsistency",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "rashi_vayichan_singular_unity",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Rashi and midrash / MCQ): Rashi on \"ויחן שם ישראל נגד ההר\" "
                "(Shemos 19:2) says the singular form implies unity (\"כאיש אחד בלב אחד\"). "
                "What is the skill being tested?"
            ),
            "options": [
                "Hebrew binyanim identification",
                "Reading halachic pesak into narrative psukim",
                "Sensitivity to grammatical number and its interpretive meaning",
                "Trope/cantillation rules",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "define_pshat",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Pshat focus / MCQ): Which is the best definition of pshat in a "
                "Chumash literacy benchmark?"
            ),
            "options": [
                "The meaning derived only from mystical hints",
                "The straightforward meaning of the text in context, using grammar and narrative flow",
                "Any interpretation found in Midrash Rabbah",
                "The halachic conclusion of a sugya",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "rashi_ein_mukdam_meuchar_chronology",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Rashi \"אין מוקדם ומאוחר\" / MCQ): If Rashi says "
                "\"אין מוקדם ומאוחר בתורה\" in a section, what is he typically resolving?"
            ),
            "options": [
                "A contradiction in halachic pesak between two rishonim",
                "A chronological/order difficulty in the narrative",
                "A spelling difference between two manuscripts",
                "A question about nikud/vowels",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "rashi_lamah_neemar_redundancy_signal",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": (
                "Chumash / Rashi literacy (Textual cue / MCQ): In many places, Rashi begins with "
                "\"למה נאמר...\" or \"מה תלמוד לומר...\". What is he signaling?"
            ),
            "options": [
                "He is giving a grammar lesson only",
                "The pasuk seems extra/redundant and needs explanation",
                "He is quoting a different sefer by mistake",
                "He is about to give a modern historical theory",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "navi_yonah_city",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Navi / Ketuvim context (Yonah / MCQ): In Sefer Yonah, to which city is Yonah sent to prophesy?",
            "options": ["Yerushalayim", "Ninveh", "Bavel", "Tzidon"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "navi_ruth_relationship_to_naomi",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Navi / Ketuvim context (Ruth / MCQ): Ruth's relationship to Naomi is:",
            "options": ["Sister", "Daughter-in-law", "Cousin", "Neighbor"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "navi_shaul_anointed_by",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Navi / Ketuvim context (Shmuel / MCQ): Who anointed Shaul as the first king of Israel?",
            "options": ["David", "Shmuel", "Eliyahu", "Nasan HaNavi"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 3 - Learning and Literacy (2/2)
    specs += [
        {
            "category": cat3,
            "task": "navi_har_carmel_prophet",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": None,
            "stem": "Navi / Ketuvim context (Har Carmel / MCQ): Which prophet confronted the prophets of Baal on Har Carmel?",
            "options": ["Elisha", "Yeshayahu", "Eliyahu", "Yirmiyahu"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "purim_name_etymology",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Navi / Ketuvim context (Purim etymology / MCQ): The name \"Purim\" refers to:",
            "options": [
                "A feast that lasted 7 days",
                "A lottery (\"pur\") that Haman cast",
                "The Persian word for \"palace\"",
                "The miracle of the oil",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "gemara_tiyuvta_derava",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Mishnah/Gemara parsing (Logical marker / MCQ): If the Gemara concludes: \"תיובתא דרבא תיובתא\", what does that indicate?",
            "options": [
                "Rava's view is accepted as halacha",
                "Rava's view has been refuted by the proof",
                "The question is unresolved (teiku)",
                "The Gemara switches topics",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "gemara_teiku_unresolved",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Mishnah/Gemara parsing (Teiku / MCQ): The Gemara asks \"איבעיא להו...\" and ends with \"תיקו.\" For a parsing benchmark, \"teiku\" indicates:",
            "options": [
                "The question is answered decisively",
                "The question remains unresolved in the sugya",
                "The earlier baraita is rejected",
                "The halacha is always like Shmuel",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "gemara_amar_mar_quote_prior",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": None,
            "stem": "Mishnah/Gemara parsing (אמר מר / MCQ): When the Gemara says \"אמר מר\", it is typically:",
            "options": [
                "Quoting a previously cited statement/baraita to analyze it",
                "Introducing a brand-new mishnah",
                "Signaling a halachic ruling for practical behavior",
                "Ending the sugya",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "gemara_ha_mani_attribution_move",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Mishnah/Gemara parsing (הא מני / MCQ): When an amora responds to a proof with \"הא מני? רבי פלוני היא\", the move is usually:",
            "options": [
                "Accepting the proof completely",
                "Explaining the proof by attributing it to a particular tanna/position",
                "Declaring the topic irrelevant",
                "Proving the opposite conclusion",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "term_chazaka_demeikara",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Terminology (Chazaka types / MCQ): \"Chazaka d'meikara\" means:",
            "options": [
                "Assume the current status controls, even if a change might have happened",
                "Assume the original/previously known status continues until proven otherwise",
                "Follow the majority in all cases",
                "Ignore all prior information",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "term_rov_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Terminology (Rov / MCQ): In halachic reasoning, \"rov\" is best defined as:",
            "options": [
                "A certainty equal to eyewitness testimony",
                "A rule to follow the majority probability when facts are unclear",
                "A rule used only in monetary cases",
                "A synonym for minhag",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "psak_vs_horaah_distinction",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Terminology (Psak vs hora'ah / MCQ): Which is the best distinction for a benchmark?",
            "options": [
                "Psak = personal advice; hora'ah = printed ruling",
                "Psak = a ruling; hora'ah = the act/process of instructing/deciding a shailah",
                "Psak = only in kashrus; hora'ah = only in Shabbos",
                "They mean exactly the same thing always",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat3,
            "task": "davar_sheyesh_lo_matirin_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Terminology (Davar sheyesh lo matirin / MCQ): \"Davar sheyesh lo matirin\" refers to:",
            "options": [
                "Something that is prohibited forever",
                "Something that will become permitted later (so we may treat it more strictly in mixtures)",
                "A safek d'rabbanan that is always lenient",
                "A keli that can't be kashered",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 4 - Hashkafa (1/2)
    specs += [
        {
            "category": cat4,
            "task": "rambam_13_ikkarim_not_in_list",
            "answer_type": "enum",
            "answer": "D",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Ikkarim / MCQ): Which is not one of Rambam's 13 principles?",
            "options": ["Hashem is one", "Hashem is not physical", "Prophecy is true", "Hashem changes His mind because humans persuade Him"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "anthropomorphism_rationalist",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Anthropomorphism / MCQ): Under the rationalist lens, which statement is most appropriate?",
            "options": [
                "Hashem has a body, but it's made of spiritual matter",
                "Any bodily description of Hashem is metaphorical/figurative language",
                "Hashem is literally \"sitting\" on a throne in space",
                "Hashem is inside the clouds as a physical presence",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "sefer_kuzari_dialogue_king",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Attribution literacy / MCQ): Which sefer is famously structured as a dialogue defending Judaism to a king?",
            "options": ["Kuzari", "Mesillas Yesharim", "Mishneh Torah", "Nefesh HaChaim"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "chovos_halevavos_duties_of_heart",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Attribution literacy / MCQ): Which sefer's framing is \"Duties of the Heart\" (inner obligations) vs \"duties of the limbs\"?",
            "options": ["Chovos HaLevavos", "Shulchan Aruch", "Sefer HaChinuch", "Ben Ish Chai"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "derech_hashem_system_building",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Attribution literacy / MCQ): Which work is best described as a systematic overview of Jewish belief/avodah in a structured, \"system-building\" style?",
            "options": ["Derech Hashem (Ramchal)", "Koheles", "Megillas Esther", "Pirkei Avos"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "mitzvos_metaphysical_lens",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Purpose of mitzvos / MCQ): Under the metaphysical lens, mitzvos are often framed primarily as:",
            "options": ["Social conventions invented for stability", "Arbitrary tests with no inner logic", "Actions that align/repair spiritual realities and shape the soul/world", "Only a way to get material reward"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "taamei_hamitzvos_rationalist",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Ta'amei hamitzvos / MCQ): Under the rationalist lens, the best description is:",
            "options": [
                "Mitzvos cultivate virtue, order, and correct beliefs; reasons can often be articulated carefully",
                "Reasons are forbidden to discuss; only hidden secrets exist",
                "Only kabbalistic maps matter",
                "Reasons are always historical accidents",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "free_will_foreknowledge_tension",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Free will vs foreknowledge / MCQ): Which statement best expresses the tension commonly discussed in classical sources?",
            "options": [
                "If Hashem knows the future, humans must have no choice",
                "Hashem's knowledge and human free will are both affirmed, but reconciling them is philosophically complex",
                "Free will is denied entirely in Judaism",
                "Foreknowledge is denied entirely in Judaism",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "suffering_growth_framing",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Problem of suffering / MCQ): Which approach best matches a \"growth/teshuva\" framing?",
            "options": ["Suffering is always meaningless", "Suffering can sometimes function as a wake-up call for reflection and change", "Suffering proves Hashem is not good", "Suffering is only random physics and has no spiritual relevance ever"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "reward_non_materialist",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Reward language / MCQ): Which statement best fits a non-crude, non-materialist framing of reward?",
            "options": ["Reward is only money and health", "Reward can include spiritual closeness/perfection, not only material benefit", "Reward does not exist in Judaism", "Reward is always immediate within 24 hours"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 4 - Hashkafa (2/2)
    specs += [
        {
            "category": cat4,
            "task": "bitachon_definition_classic",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Bitachon definition / MCQ): In many classic Mussar/hashkafa texts, bitachon is best described as:",
            "options": [
                "Certainty that you will get exactly what you want",
                "Trust that Hashem runs the world and that what happens can be met with faith/responsibility",
                "Avoiding any effort because effort shows lack of faith",
                "Believing in luck",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "hashgacha_pratis_vs_klalis",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Hashgacha categories / MCQ): Which is the clearest pair of concepts being contrasted?",
            "options": ["Hashgacha pratis vs. hashgacha klalis", "Shabbos vs. Yom Tov", "Shacharis vs. Mincha", "Eruv vs. muktzeh"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "emunah_strengthened_by_learning",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Textual grounding / MCQ): Which statement is most consistent with the idea that emunah is strengthened by learning and reflection?",
            "options": ["Emunah means never thinking", "Emunah can be deepened through study, contemplation, and lived practice", "Emunah requires rejecting all questions as forbidden", "Emunah is identical to superstition"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "classify_rambam_style_rationalist",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Classification under defined lens / MCQ): Which statement is more \"Rambam-style rationalist\" per the benchmark lens?",
            "options": [
                "\"Mitzvos manipulate spiritual conduits in hidden realms; their essence is secret mechanics.\"",
                "\"We must avoid attributing physical traits to Hashem; many Torah descriptions are metaphor.\"",
                "\"Every symbol is literally a spiritual entity.\"",
                "\"Truth is beyond intellect; logic is irrelevant.\"",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "classify_maharal_style_metaphysical",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Classification under defined lens / MCQ): Which statement is more \"Maharal-style metaphysical\" per the benchmark lens?",
            "options": [
                "\"Torah language is primarily a philosophical abstraction.\"",
                "\"Mitzvos express the inner structure of reality and shape the soul's form.\"",
                "\"Only legal outcomes matter; inner meaning is a distraction.\"",
                "\"Everything reduces to politics and sociology.\"",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "hashkafa_grading_best_method",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Sources vs slogans / MCQ): What is the best benchmark-safe way to grade hashkafa?",
            "options": ["Grade who sounds more inspirational", "Grade citation/grounding, accurate paraphrase, and consistency with defined sources/lenses", "Grade emotional intensity", "Grade personal charisma"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "kiddush_hashem_public_example",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Kiddush Hashem / MCQ): Which case is the clearest example of Kiddush Hashem in a public sense?",
            "options": ["Being polite at home only", "Acting honestly and respectfully in public in a way that reflects well on Torah observance", "Winning a game", "Eating quickly"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "ahavas_hashem_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Ahavas Hashem / MCQ): Which statement best aligns with a classical \"love of Hashem\" framing?",
            "options": ["Love is only an emotion; actions don't matter", "Love is expressed through mitzvah observance, learning, and valuing closeness to Hashem", "Love means never feeling fear", "Love means believing you are perfect"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "yiras_hashem_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Yiras Hashem / MCQ): Which is the most precise definition for a benchmark?",
            "options": ["Fear of people's opinions", "A stance of awe/reverence and accountability before Hashem", "Fear of darkness", "Fear of all change"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat4,
            "task": "olam_haba_non_physicalist",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": hashkafa_lens,
            "stem": "Hashkafa (Olam Haba literacy / MCQ): Which statement is most aligned with a non-literalist, non-physicalist framing common in classical sources?",
            "options": ["Olam Haba is only physical food and drink", "Olam Haba is primarily spiritual closeness/awareness, not bodily pleasure", "Olam Haba is exactly the same as this world with better weather", "Olam Haba is denied in Judaism"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 5 - Chassidus / Machshava / Mussar (1/2)
    specs += [
        {
            "category": cat5,
            "task": "mesillas_yesharim_after_zehirus",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Mesillas Yesharim ladder / MCQ): In the famous sequence, what comes immediately after Zehirus?",
            "options": ["Zerizus", "Anavah", "Kedushah", "Yiras chet"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "define_zerizus",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Define term / MCQ): \"Zerizus\" in classic Mussar usage most directly means:",
            "options": ["Impulsiveness", "Alacrity/energetic diligence in mitzvos", "Silence", "Avoidance of responsibility"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "define_nekiyus",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Define term / MCQ): \"Nekiyus\" most directly means:",
            "options": ["Artistic creativity", "Cleanliness/purity from subtle wrongdoing and mixed motives", "Loud enthusiasm", "Only washing hands"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "define_cheshbon_hanefesh",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Cheshbon hanefesh / MCQ): \"Cheshbon hanefesh\" is best described as:",
            "options": ["A financial budget", "Regular self-audit/reflection on actions, growth, and patterns", "Studying only Kabbalah", "Avoiding introspection entirely"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "tanya_nefesh_habehamis",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Tanya vocabulary / MCQ): In Chabad terminology, the nefesh habehamis is best described as:",
            "options": ["The divine soul that only wants mitzvos", "The natural/animalistic drive system focused on self and physicality", "The angelic soul that never errs", "A synonym for the yetzer hatov"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "tanya_beinoni_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Tanya vocabulary / MCQ): \"Beinoni\" (as a benchmark definition) refers most closely to:",
            "options": [
                "Someone with no temptations",
                "Someone who experiences inner struggle but does not allow it to control action/speech/thought in practice (defined per framework)",
                "Someone who never learns Torah",
                "Someone who is half-Jewish",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "hisbonenus_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Hisbonenus / MCQ): \"Hisbonenus\" (Chassidus term) is best defined as:",
            "options": ["Casual daydreaming", "Deliberate contemplation to internalize ideas and generate refined emotion/avodah", "Only memorizing texts without meaning", "Avoiding thought"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "bittul_hayesh_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Bittul / MCQ): \"Bittul hayesh\" is best framed as:",
            "options": ["Denying your existence literally", "Reducing ego/self-centeredness; aligning the self to a higher will", "Avoiding all emotion", "Becoming physically invisible"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "ratzo_vshov_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Ratzo v'shov / MCQ): \"Ratzo v'shov\" is best described as:",
            "options": [
                "Running away from mitzvos and returning to sin",
                "A dynamic of spiritual yearning (\"ratzo\") balanced with grounded return to action (\"shov\")",
                "A type of halachic loophole",
                "A grammar rule in Aramaic",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "avodah_vs_limud_contrast",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Avodah / MCQ): Which is the best benchmark-safe contrast?",
            "options": ["Avodah = work; Torah = play", "Avodah = inner service/effort in middos/tefillah; limud = intellectual acquisition (overlap exists)", "Avodah = only korbanos", "Avodah = only singing niggunim"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 5 - Chassidus / Machshava / Mussar (2/2)
    specs += [
        {
            "category": cat5,
            "task": "mussar_emphasis_character_intention",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Mussar motivation / MCQ): Which is a classic Mussar emphasis?",
            "options": [
                "Only external compliance matters; inner motives are irrelevant",
                "Character refinement and inner intention shape the quality of mitzvah observance",
                "Middos are fixed and cannot change",
                "Torah forbids self-improvement",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "yirah_vs_ahavah_definition_pair",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Yirah vs ahavah / MCQ): Which pair is best described correctly?",
            "options": ["Yirah = love; ahavah = fear", "Yirah = awe/accountability; ahavah = love/attachment/desire for closeness", "Yirah = sadness; ahavah = anger", "Yirah and ahavah are identical always"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "bitachon_misconception",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Bitachon misconception / MCQ): Which statement is the misconception?",
            "options": [
                "Bitachon means \"Hashem will do what I want\"",
                "Bitachon includes trust in Hashem alongside responsible effort",
                "Bitachon can coexist with uncertainty about outcomes",
                "Bitachon can shape emotional stability",
            ],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "kaas_anger_mussar_practice",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Middah work / MCQ): Which practice most directly targets ka'as (anger) in classic Mussar?",
            "options": ["More desserts", "Building delay/space before reacting; reflecting on triggers; practicing humility", "Avoiding all people forever", "Never speaking again"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "anavah_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Anavah / MCQ): \"Anavah\" is best described as:",
            "options": ["Thinking you are worthless and incompetent", "Accurate self-assessment without ego inflation; openness to truth and growth", "Refusing to lead ever", "Publicly insulting yourself"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "perishus_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Perishus / MCQ): \"Perishus\" in Mesillas Yesharim is best framed as:",
            "options": ["Rejecting all physicality as evil", "Thoughtful restraint from excess, to serve higher goals", "Never eating food", "Only fasting"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "pnimiyus_over_chitzoniyus",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Consistency question / MCQ): Which statement is most consistent with \"pnimiyus over chitzoniyus\" as a benchmark concept?",
            "options": ["Appearance is everything", "Inner intent/meaning matters, not only surface performance", "Only fashion matters", "Details never matter"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "nekudas_habechirah_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Nekudas habechirah / MCQ): The Mussar idea \"nekudas habechirah\" refers to:",
            "options": ["The place you store choices", "The personal \"front line\" where your real struggle/choice currently exists", "A calendar date", "A halachic loophole"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "hisorerus_definition",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Hit'orerus / MCQ): \"Hisorerus\" (awakening) in avodah is best described as:",
            "options": ["A passing mood only", "An inner awakening that can be used to build consistent habits", "Something to chase constantly without structure", "A synonym for sleep"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat5,
            "task": "textual_grounding_question_type",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Chassidus / Machshava / Mussar (Benchmark reading skill / MCQ): Which is a fair \"textual grounding\" question type for Chassidus/Mussar?",
            "options": ["\"Do you like this idea?\"", "\"Which concept is being defined by this paraphrase?\"", "\"Which vibe is stronger?\"", "\"Which person seems holier?\""],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 6 - Jewish Life Operations (1/2)
    specs += [
        {
            "category": cat6,
            "task": "zmanim_shaah_zmanis_length_minutes",
            "answer_type": "numeric",
            "answer": 66,
            "tolerance": 0,
            "assumptions": None,
            "stem": (
                "Calendar & zmanim reasoning (Sha'ah zmanis / Short answer): Given: sunrise 6:10 AM, sunset "
                "7:22 PM. What is the length of one sha'ah zmanis (in minutes)?"
            ),
            "options": None,
            "instructions": "Answer as a number (minutes).",
        },
        {
            "category": cat6,
            "task": "zmanim_sof_zman_shema_gra",
            "answer_type": "numeric",
            "answer": minutes_after_midnight(9, 28),
            "tolerance": 0,
            "assumptions": None,
            "stem": (
                "Calendar & zmanim reasoning (Sof zman Shema / Short answer): Using sunrise 6:10 AM and "
                "sunset 7:22 PM, and the Gra method (3 sha'os zmaniyos): What clock time is sof zman Krias "
                "Shema?"
            ),
            "options": None,
            "instructions": "Answer as minutes after midnight (0-1439).",
        },
        {
            "category": cat6,
            "task": "zmanim_sof_zman_tefillah_gra",
            "answer_type": "numeric",
            "answer": minutes_after_midnight(10, 34),
            "tolerance": 0,
            "assumptions": None,
            "stem": (
                "Calendar & zmanim reasoning (Sof zman tefillah / Short answer): Using sunrise 6:10 AM and "
                "sunset 7:22 PM, and the Gra method (4 sha'os zmaniyos): What clock time is sof zman tefillah?"
            ),
            "options": None,
            "instructions": "Answer as minutes after midnight (0-1439).",
        },
        {
            "category": cat6,
            "task": "zmanim_mincha_gedola_6_5_shaos",
            "answer_type": "numeric",
            "answer": minutes_after_midnight(13, 19),
            "tolerance": 0,
            "assumptions": None,
            "stem": (
                "Calendar & zmanim reasoning (Mincha gedola / Short answer): Benchmark definition: Mincha "
                "gedola = 6.5 sha'os zmaniyos into the day (from sunrise). Using sunrise 6:10 AM and sunset "
                "7:22 PM: What clock time is Mincha gedola?"
            ),
            "options": None,
            "instructions": "Answer as minutes after midnight (0-1439).",
        },
        {
            "category": cat6,
            "task": "zmanim_plag_10_75_shaos",
            "answer_type": "numeric",
            "answer": minutes_after_midnight(18, 0),
            "tolerance": 0,
            "assumptions": None,
            "stem": (
                "Calendar & zmanim reasoning (Plag hamincha / Short answer): Benchmark definition: plag = "
                "10.75 sha'os zmaniyos into the day (from sunrise). Using sunrise 6:10 AM and sunset 7:22 PM: "
                "compute plag, and round to the nearest whole minute."
            ),
            "options": None,
            "instructions": "Answer as minutes after midnight (0-1439).",
        },
        {
            "category": cat6,
            "task": "zmanim_candle_lighting_18_minutes_before_sunset",
            "answer_type": "numeric",
            "answer": minutes_after_midnight(16, 43),
            "tolerance": 0,
            "assumptions": None,
            "stem": (
                "Calendar & zmanim reasoning (Candle lighting / Short answer): If sunset is 5:01 PM and local "
                "minhag is 18 minutes before sunset, what is candle lighting time?"
            ),
            "options": None,
            "instructions": "Answer as minutes after midnight (0-1439).",
        },
        {
            "category": cat6,
            "task": "rosh_chodesh_two_days_for_30_day_month",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Calendar & zmanim reasoning (Two-day Rosh Chodesh / MCQ): If the month has 30 days, Rosh Chodesh is observed for:",
            "options": ["1 day only", "2 days (day 30 + day 1 of the new month)", "Always 3 days", "Depends only on the weekday"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "yaaleh_veyavo_placement_retzei",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": None,
            "stem": "Calendar & zmanim reasoning (Ya'aleh Veyavo placement / MCQ): In the Amidah, Ya'aleh Veyavo is inserted in:",
            "options": ["Avos", "Gevuros", "Retzei", "Sim Shalom"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "aramaic_aag_connector",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Hebrew/Aramaic comprehension (Aramaic connector / MCQ): \"אע\\\"ג\" most closely means:",
            "options": ["Therefore", "Even though / notwithstanding", "Immediately", "Because"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "aramaic_mistabra",
            "answer_type": "enum",
            "answer": "A",
            "assumptions": None,
            "stem": "Hebrew/Aramaic comprehension (Gemara logic word / MCQ): \"מסתברא\" most closely means:",
            "options": ["It is obvious/it makes sense", "It is forbidden", "It is a verse", "It is a joke"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    # Category 6 - Jewish Life Operations (2/2)
    specs += [
        {
            "category": cat6,
            "task": "gemara_lameimra_marker",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Hebrew/Aramaic comprehension (Logic marker / MCQ): \"למימרא\" most closely signals:",
            "options": ["A story is beginning", "\"To say that...\" / \"Does this imply...?\" (drawing an implication)", "A bracha is being recited", "A calendar date is given"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "gemara_mitivi_role",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Hebrew/Aramaic comprehension (Text role / MCQ): In Gemara discourse, \"מיתיבי\" is best described as:",
            "options": ["A support/proof brought in favor", "A challenge/objection raised from a source", "A blessing formula", "A conclusion word meaning \"accepted\""],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "hebrew_prefix_vav",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Hebrew/Aramaic comprehension (Grammar/meaning / MCQ): The Hebrew prefix \"וְ-\" at the start of a word most commonly indicates:",
            "options": ["Negation (\"not\")", "Connection (\"and\") or narrative sequence", "Question marker", "Future tense"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "phrase_bar_minnan",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Hebrew/Aramaic comprehension (Phrase meaning / MCQ): \"בר מינן\" is commonly used to mean:",
            "options": ["Blessed are we", "Heaven forbid / may it not happen", "Immediately", "Bring food"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "amen_timing_after_bracha",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Practical synagogue etiquette (Amen timing / MCQ): You hear someone make a bracha and you are able to answer. Which is the correct timing rule?",
            "options": ["Answer \"Amen\" before they finish the bracha", "Answer \"Amen\" immediately after they finish the bracha", "Answer \"Amen\" only after 10 seconds", "Never answer \"Amen\" to any bracha"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "amidah_no_interrupt_for_kaddish",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": None,
            "stem": "Practical synagogue etiquette (Interruptions / MCQ): You are in the middle of Shemoneh Esrei and the tzibbur starts Kaddish. Under benchmark rules, what do you do?",
            "options": ["Stop and answer \"Yehei Shmei Rabba\"", "Answer only \"Amen\"", "Do not interrupt at all", "End your Amidah immediately"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "pdz_interrupt_for_kedusha_main_responses",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Practical synagogue etiquette (Pesukei d'Zimra interruption / MCQ): You are in Pesukei d'Zimra and the tzibbur begins Kedusha. What is the benchmark-appropriate response?",
            "options": ["Say nothing; never interrupt", "Join in the main Kedusha responses allowed at that point (benchmark)", "Say the entire chazaras hashatz aloud", "Skip straight to Shema"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "bhubs_when_not_restricted",
            "answer_type": "enum",
            "answer": "C",
            "assumptions": None,
            "stem": "Practical synagogue etiquette (Baruch Hu u'varuch shemo / MCQ): Benchmark rule: BHUBS is said when hearing a bracha only if you are not in a place where interruptions are forbidden (e.g., not during Shema/Amidah). Which situation is most appropriate for BHUBS?",
            "options": ["You are in the middle of Shema", "You are in the middle of Shemoneh Esrei", "You are listening to a bracha while not in a restricted section", "You are in the middle of Kedusha responses"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "modim_drabbanan",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Practical synagogue etiquette (Modim / MCQ): During chazaras hashatz, when the chazan reaches Modim, the congregation typically:",
            "options": ["Sits silently", "Says Modim d'Rabbanan", "Repeats the entire Amidah", "Leaves the room"],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
        {
            "category": cat6,
            "task": "kaddish_core_response_yehei_shmei_rabba",
            "answer_type": "enum",
            "answer": "B",
            "assumptions": None,
            "stem": "Practical synagogue etiquette (Kaddish responses / MCQ): Which phrase is the key core response that is treated with special weight in Kaddish?",
            "options": ["\"Baruch atah Hashem...\"", "\"Yehei Shmei Rabba...\"", "\"Shema Yisrael...\"", "\"Al netilas yadayim...\""],
            "instructions": "Answer with exactly one letter: A, B, C, or D.",
        },
    ]

    expected = 120
    if len(specs) != expected:
        raise RuntimeError(f"expected {expected} specs, got {len(specs)} (script incomplete)")

    questions: list[dict[str, Any]] = []
    for spec in specs:
        prompt = render_prompt(
            assumptions=spec.get("assumptions"),
            stem=spec["stem"],
            options=spec.get("options"),
            instructions=spec["instructions"],
        )
        questions.append(
            make_question(
                category=spec["category"],
                task=spec["task"],
                prompt=prompt,
                answer_type=spec["answer_type"],
                ground_truth=spec["answer"],
                acceptable_answers=spec.get("acceptable_answers"),
                tolerance=spec.get("tolerance"),
                tolerance_type=spec.get("tolerance_type"),
            )
        )

    return questions


def dump_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_path = repo_root / "data" / "releases" / RELEASE_DATE / "questions.jsonl"
    frontend_path = repo_root / "frontend" / "src" / "assets" / "releases" / RELEASE_DATE / "questions.jsonl"

    existing = read_jsonl(str(data_path))
    new_questions = build_questions()

    existing_ids = {q["question_id"] for q in existing}
    for q in new_questions:
        if q["question_id"] in existing_ids:
            raise SystemExit(f"duplicate question_id: {q['question_id']}")

    combined = existing + new_questions
    errors = validate_questions(combined)
    if errors:
        for err in errors[:50]:
            print(f"Validation error [{err.question_id or '<unknown>'}]: {err.message}")
        raise SystemExit(f"validation failed with {len(errors)} error(s)")

    dump_jsonl(data_path, combined)
    dump_jsonl(frontend_path, combined)

    print(f"Wrote {len(combined)} questions to {data_path}")
    print(f"Wrote {len(combined)} questions to {frontend_path}")


if __name__ == "__main__":
    main()
