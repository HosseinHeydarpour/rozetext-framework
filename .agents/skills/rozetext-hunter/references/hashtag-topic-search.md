# Hashtag and topic search system for @rozetext.ir

Purpose: find Persian written-text reels **beyond the 120 benchmark accounts**, plus
English written-text material that can be translated into the page's voice.
This is a search system, not a hunt report: no candidate has been scored from
these lists yet, and no hashtag popularity number is claimed here. Third-party
hashtag-count sites disagree with each other and are dated, so this file uses
only qualitative labels — broad / niche / noisy — and says where each term
comes from.

Standing rules that apply unchanged (from the hunter skill):
- Browser only, logged in as `hosseinheydarpour`. No Instagram API hunting.
- Read the in-video text from frames, line by line. Never the caption, never a guess.
- Caption-only or incomplete text = reject. Spoken declamation with no readable
  on-screen text = reject (unless it is audio-transcribed, which is a separate step).
- Persona filter, full-history anti-duplication (history #1–#384) and mandatory
  engine scoring (`evaluate_script_v3`, no guesswork) apply to every hashtag find,
  exactly as to every account find.
- Stop and report on any CAPTCHA or temporary limit.

Pillars (v4.1): P1 بغض و خستگی بی‌صدا · P2 خداحافظی باوقار و پذیرش پایان ·
P3 آدم امن و تقدیم‌نامه · P4 مرزبندی و گلایه باوقار · P5 مانیفست اصالت،
رفتاربینی و عدالت · P6 مینی‌روایت، دیالوگ و نوستالژی · P7 خانواده، امید و آرامش.

---

## 1. Persian hashtags and search phrases (60 entries)

### 1a. Format-first tags — use with a pillar tag, never alone (12)

These say "this is a text reel", not what it is about. They are the highest-yield
starting points, and also the noisiest: they mix text reels with static
photo-texts, story screenshots, humour and song clips. Always pair with a
pillar tag from §1b, or filter by opening tiles only.

| # | Tag | Surfaces | Noise to avoid |
|---|---|---|---|
| 1 | #تکست | Written-text reels and photo-texts, all themes | Humour, memes, song lyrics, motivational posters |
| 2 | #تکست_خاص | Curated "special" texts, often longer and first-person | Reposts of the same viral texts; check anti-duplication first |
| 3 | #تکست_ناب | "Pure" texts; overlaps the page's own caption vocabulary | Generic positivity posters |
| 4 | #دلنوشته | Diary-style first-person texts, all pillars | Long book excerpts, second-person advice |
| 5 | #دلنوشته_خاص | Longer curated diary texts | Preachy / yellow-psychology advice |
| 6 | #دلنوشته_ناب | Short, clean diary texts | Static images with no reel |
| 7 | #متن_سنگین | Heavy, quotable texts — closest to the page's core | Aggressive "تیکه" texts that fail the dignity filter |
| 8 | #متن_کوتاه | Short cards; good for slot 1 and short-text checks | Too short for the 45–80 word target; many are one-liners |
| 9 | #حرف_دل | Heart-talk texts, P1/P3 heavy | Song clips and spoken declamation |
| 10 | #تکستگرافی | Designed text graphics, often as reels | Design-led posts where text is decoration, not content |
| 11 | #متن_احساسی | Emotional texts, broad | Crying-face / melodrama clips, second-person longing without dignity |
| 12 | #دلنوشته_غمگین | Sad diary texts, P1/P2 heavy | Pure grief without a boundary or a turn; check for a mic-drop line |

Sources for §1a: these tags appear together in Persian hashtag directories
(e.g. the Flick related-tags list for #تکست_لاو: #تکست، #تکست_خاص، #حرف_دل،
#دلنوشته_خاص، #متن_کوتاه، #تکستگرافی، #متن_احساسی، #دلنوشته_غمگین) and in
the page's own caption vocabulary (#تکست_ناب، #متن_سنگین).

### 1b. Pillar tags and phrases (48: 7 pillars × ~7, minus one)

Each row is either a hashtag (H) or an Instagram search phrase (P). Phrases are
typed into Instagram search, not used as hashtags; they catch reels whose
caption or on-screen text contains the phrase even when the poster used no
pillar tag.

#### P1 — بغض و خستگی بی‌صدا (7)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #تنهایی | H | Loneliness texts, first-person | "تنهایی" music clips, couple photos |
| #دلمگرفته | H | Heavy-heart texts, P1 core | Melodrama, crying reels with no text |
| #فاز_سنگین | H | Heavy-mood texts | Aggressive or drug-adjacent slang posts |
| #تکست_دپ | H | "Dep" mood texts, short and raw | Very short / slang-only cards |
| #تکست_غمگین | H | Sad texts, P1/P2 border | Pure grief with no turn |
| #غمگین | H | Broad sad content | Music-only sad reels |
| «خسته‌ام اما» | P | Tired-but-standing texts (the P1 stance) | Complaint lists with no dignity |

#### P2 — خداحافظی باوقار و پذیرش پایان (7)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #رفت | H | Leaving / gone texts | Song clips titled "رفت" |
| #مرگ_احساس | H | Dead-feeling / ended-love texts | Over-dramatic revenge texts |
| #عاشقانه_تلخ | H | Bitter-love texts, P2/P4 border | Second-person blame rants |
| #شکستن_دل | H | Heartbreak texts | Curse / revenge texts (persona veto) |
| #خداحافظی | H | Farewell texts | Farewell-to-a-place / travel posts |
| «دیگر برنمی‌گردم» | P | Dignified no-return lines | Angry "never again" rants |
| «پذیرفتم که» | P | Acceptance turns, the P2 mic-drop shape | Advice posts ("بپذیر که…") in second person |

#### P3 — آدم امن و تقدیم‌نامه (7)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #آدم_امن | H | Safe-person texts; already in the page's captions | Couple-photo dedications with no text |
| #پناه | H | Shelter / refuge texts | Religious-only shelter posts |
| #رفیق | H | Friend-dedication texts | Friendship humour / memes |
| #همراه | H | Companion texts | Travel-companion posts |
| #قدردانی | H | Gratitude texts | Thank-you-note clichés |
| «تو همون آدمی» | P | Safe-person dedications (proven Sunday/Saturday theme) | Song lyrics with the same line |
| «قدر محبت» | P | Gratitude-for-kindness texts (proven Saturday slot 1 theme) | Advice about gratitude, not a text |

#### P4 — مرزبندی و گلایه باوقار (7)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #حد_و_مرز | H | Boundary texts; already in the page's captions | Psychology-advice carousels |
| #احترام | H | Respect / disrespect texts | Generic respect posters |
| #مرز | H | Boundary lines, short and sharp | Political "border" posts — check the tile before opening |
| #تکست_تیکه_دار | H | Sharp comeback texts | Aggressive, insulting or cursing texts (persona veto) |
| #تیکه_ناب | H | Quotable sharp lines | Humour roasts |
| «دیگر توضیح نمی‌دهم» | P | Boundary-without-explanation lines | Arguments / drama clips |
| «وظیفه‌ام نیست» | P | "Not my duty" boundary texts (proven theme family) | Complaint rants |

#### P5 — مانیفست اصالت، رفتاربینی و عدالت (7)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #اصالت | H | Authenticity manifesto texts | Luxury / "original product" posts |
| #معرفت | H | Character / معرفت texts; in the page's captions | Preachy moralising |
| #پختگی | H | Maturity texts; in the page's captions | Age-based advice posts |
| #خودت_باش | H | Be-yourself texts | Selfie captions, no text reel |
| #تکست_ناب | H | (Also format-first) quotable manifesto lines | Generic positivity |
| «من همینم» | P | I-am-this authenticity lines | Defiant / arrogant tone (check dignity) |
| «از یه سنی به بعد» | P | Milestone-hook texts; also an engine +6 bonus phrase | Reposts — anti-duplication check is critical here |

#### P6 — مینی‌روایت، دیالوگ و نوستالژی (7)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #داستان_کوتاه | H | Short-story texts, dialogue-led | Storytelling advice, book promos |
| #نوستالژی | H | Nostalgia texts | Old-photo dumps with no text |
| #خاطره | H | Memory texts | Photo-memory posts, wedding clips |
| #دلنوشته_ها | H | Diary-story texts | Long multi-part stories (too long for one reel) |
| #گذشته | H | Past / past-love texts | Throwback photo posts |
| «یادته» | P | "Do you remember" dialogue openings | Song clips, nostalgia memes |
| «یه زمانی» | P | "There was a time" narrative openings; engine bonus family | Book excerpts (borderline — check originality note) |

#### P7 — خانواده، امید و آرامش (6)

| Tag / phrase | Type | Surfaces | Noise to avoid |
|---|---|---|---|
| #خانواده | H | Family texts | Family photos with no text |
| #امید | H | Hope texts, slot-1 friendly | Generic hope posters, religious-only posts |
| #آرامش | H | Calm texts; in the page's captions | Meditation music, no text |
| #مادر | H | Mother texts | Mother's-day photo dumps |
| #پدر | H | Father texts | Same as above |
| «هنوز امید هست» | P | Hope-after-hardship turns | Slogan-only cards |

Total Persian list: 12 format-first + 48 pillar entries = **60**.

---

## 2. English hashtags and phrases for translation (42 entries)

Rules for this list, before any translation happens:
- **TEXT-FIRST** = the tag is dominated by readable on-screen text, carousels
  or captioned text reels. These are the only tags to hunt first.
- **MIXED** = text reels sit alongside voiceover, face-to-camera and static
  quote images. Open tiles only; reject anything whose text cannot be read
  frame by frame.
- **SPOKEN-FIRST — do not hunt** = the tag is dominated by performed,
  spoken-word delivery. Spoken word is written for the ear and for performance,
  not for the eye, so a spoken-only reel cannot become a RozeText text reel
  without a full transcription step, which is out of scope for hunting.
  These rows are listed so hunters recognise and skip them, not as targets.
- A translated text is **not** a raw copy: it goes through the (separate)
  translation-and-writing guide for the page's voice, then through the same
  persona filter, anti-duplication check and mandatory engine scoring as a
  Persian find. Never publish a literal translation that sounds translated.
- Skip: song lyrics, attributed famous quotes (fabricated-quotation veto),
  humour/meme accounts, and anything preachy or "5 steps to happiness".

Sources for §2: English poetry/writing tags appear together in hashtag
directories (Flick for #poetry: #quotes, #poetrycommunity, #writersofinstagram,
#poetsofinstagram, #words, #wordporn, #instapoetry, #poetryofinstagram,
#writerscommunity, #poemsofinstagram, #micropoetry, #poetrylovers; IQHashtags
for #boundaries and #selfawareness: #boundaries, #selflove, #healing,
#healingjourney, #selfworth, #innerpeace, #authenticity, #selfrespect,
#gratitude, #relationships; breakup-caption sources: #MovingOn, #HeartHealing,
#SelfLoveJourney, #lettinggo family).

### 2a. Format-first English tags (10)

| Tag | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #poetrycommunity | MIXED | Poem reels and carousels, all themes | Spoken performances, promo for books |
| #poetryofinstagram | TEXT-FIRST | On-screen poem texts, often carousel-first | Very short one-line poems |
| #poemsofinstagram | TEXT-FIRST | Short complete poems as text | Static images with tiny text |
| #instapoetry | MIXED | Instagram-native poems, text and voice | Face-to-camera readings |
| #writersofinstagram | MIXED | Writer texts, prose and poetry | Writing-advice posts |
| #writerscommunity | MIXED | Community writing, prose-heavy | Prompts and challenges, not finished texts |
| #micropoetry | TEXT-FIRST | Very short complete texts; good for short slots | Too short for 45–80 words — use only as slot-1/short candidates |
| #wordporn | TEXT-FIRST | Quotable single lines and short texts | One-liners, no narrative |
| #quotes | MIXED | Quote texts, broadest pool | Attributed celebrity quotes, memes, humour |
| #quoteoftheday | MIXED | Daily quote texts | Motivational-poster clichés |

### 2b. Pillar English tags and phrases (32)

#### P1 — quiet pain / exhaustion (5)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #sadpoetry | MIXED | Sad poem texts | Spoken readings, music-only reels |
| #healingquotes | TEXT-FIRST | Healing-after-pain texts | "Good vibes only" posters |
| "quiet grief" quotes | Phrase | Grief-without-noise texts | Funeral / memorial posts |
| "tired but still here" | Phrase | Exhausted-but-standing texts (P1 stance) | Burnout-advice carousels |
| #lonelinesspoetry | MIXED | Loneliness poem texts | Song clips |

#### P2 — dignified farewell / acceptance (5)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #breakupquotes | MIXED | Breakup texts | Revenge / "savage" captions (persona veto) |
| #MovingOn | MIXED | Moving-on texts | Selfie "new me" posts |
| #HeartHealing | TEXT-FIRST | Healing-after-ending texts | Therapy-advice posts |
| #lettinggo | MIXED | Letting-go texts | Advice lists ("how to let go") |
| "letting go with love" | Phrase | Dignified-release texts, the P2 turn | Preachy advice |

#### P3 — safe person / dedication (5)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #lovequotes | MIXED | Love/dedication texts, broadest P3 pool | Couple photos, wedding content |
| #safeplace | MIXED | Safe-person / safe-place texts | Home-décor posts |
| #youareenough | TEXT-FIRST | Worth/dedication lines | Selfie captions |
| "letter to my sister" | Phrase | Sibling dedication texts | Actual letters / crafts |
| "for the person who stayed" | Phrase | Dedication to the one who stayed | Wedding vows |

#### P4 — boundaries / dignified complaint (5)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #boundaries | MIXED | Boundary texts; also therapy/coach content | Coach advice carousels, no text reel |
| #selfrespect | TEXT-FIRST | Self-respect manifesto lines | Slogans only |
| #BaddieWithBoundaries | MIXED | Sharp boundary texts | Aggressive / insult tone (check dignity) |
| "not my job to" | Phrase | "Not my duty" boundary lines | Workplace humour |
| "I stopped explaining myself" | Phrase | Boundary-without-explanation texts | Rant videos |

#### P5 — authenticity / behaviour / justice (4)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #authenticity | MIXED | Be-real manifesto texts | Branding / business authenticity |
| #selfworth | TEXT-FIRST | Worth manifesto lines | Slogans only |
| #beyourself | MIXED | Be-yourself texts | Selfie captions |
| "I am not for everyone" | Phrase | Authenticity-with-boundary lines | Arrogant tone (check dignity) |

#### P6 — mini-narrative / dialogue / nostalgia (4)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #storytelling | MIXED | Story-led texts | Brand storytelling, marketing |
| #nostalgia | MIXED | Nostalgia texts | Retro photo dumps, no text |
| "do you remember when" | Phrase | Dialogue/memory openings | Song clips, memes |
| #letters | MIXED | Letter-form texts | Calligraphy art, no readable text |

#### P7 — family / hope / calm (4)

| Tag / phrase | Mode | Surfaces | Noise to avoid |
|---|---|---|---|
| #familyquotes | TEXT-FIRST | Family texts | Family photos, no text |
| #hopequotes | TEXT-FIRST | Hope texts, slot-1 friendly | Slogans only |
| #innerpeace | MIXED | Calm texts | Meditation music, yoga posts |
| #healingjourney | MIXED | Healing-journey texts | Recovery vlogs, face-to-camera |

### 2c. Spoken-first tags — recognise and skip (not counted in the 42)

| Tag | Why skip |
|---|---|
| #spokenword | Performed delivery; text is usually not fully on screen |
| #poetryinmotion | Performance-led reels |
| #slampoetry | Stage performance, not a text reel |
| #shayari | Often recited; also a language mismatch for direct hunting — use only if a full on-screen text is readable |

Total English list: 10 format-first + 32 pillar entries = **42** (plus 4
spoken-first tags listed only as do-not-hunt).

---

## 3. Hashtag hunting protocol

### 3.1 One session (about 30–45 minutes, browser only)

1. Pick **one pillar** and **2–3 tags** for it: one format-first tag plus one or
   two pillar tags, or one pillar tag plus one search phrase. Never hunt all
   seven pillars in one session — hashtag pages repeat the same viral tiles
   and the session degrades into re-checking.
2. Open the hashtag page in the logged-in browser session. Scroll in the same
   deep-scroll discipline as account hunting (roughly 15 deep-scroll steps,
   pausing for loading). Do not stop at the "Top posts" row: top posts are
   already the most-reposted texts and the most likely anti-duplication
   failures. Work the recent / chronological grid as well.
3. Open tiles that look like written-text reels. For each, read the in-video
   text from several frames, line by line. Reject on: caption-only text,
   incomplete text, spoken-only delivery, humour/meme, preaching, fabricated
   quotations, aggression, second/third-person narration, or passive longing
   without dignity or a boundary — the same vetoes as account hunting.
4. For every kept candidate, record: hashtag/phrase that surfaced it, source
   account, reel link, pillar, and whether the account is already a benchmark
   account (see §3.2). Then run the mandatory engine score and the
   full-history anti-duplication check before it is offered for any slot.
5. Stop on CAPTCHA or temporary limit and report it. Do not switch to the
   Instagram API to work around it.

### 3.2 How this plugs into account hunting without duplicating it

- **Hashtag finds from a benchmark account are account finds.** If the source
  account is already in the 120 (soon 200) benchmark list, log the candidate
  under that account, not under the hashtag, and do not count it as a
  hashtag-only discovery. This keeps the two funnels from double-counting the
  same reel.
- **Hashtag finds from a new account are the benchmark-expansion feed.**
  A new account that yields a kept, scored candidate goes on the candidate
  list for the benchmark expansion (the separate 80-account task). It does
  not become a benchmark by one reel alone; it becomes a benchmark when it
  repeatedly yields persona-fitting texts.
- **One shared seen-list.** Every reel link opened in a hashtag session goes
  on the same seen-list as account hunting, so a later account hunt does not
  re-open and re-score it. A reel found by both routes is scored once.
- **Rotation, not repetition.** Keep a simple log (date, pillar, tags used,
  tiles opened, candidates kept). Do not re-hunt the same tag + pillar
  combination within 7 days; hashtag pages turn over slowly and re-hunting
  them burns the session on tiles already rejected. Rotate pillars across
  the week so all seven get a hashtag pass before any pillar gets a second one.
- **English finds are a separate queue.** An English candidate that passes
  the text-first and persona checks goes to the translation queue, not
  directly into a pack. Only after translation into the page's voice, and a
  fresh engine score on the Persian text, can it enter a pack — and it is
  then logged as a translated find, with its English source link kept.

### 3.3 Weekly rotation template (copy into the hunt log)

| Weekday | Pillar | Tags / phrases | Tiles opened | Kept | Engine-scored | Notes |
|---|---|---|---|---|---|---|
| Sat | P1 | | | | | |
| Sun | P2 | | | | | |
| Mon | P3 | | | | | |
| Tue | P4 | | | | | |
| Wed | P5 | | | | | |
| Thu | P6 | | | | | |
| Fri | P7 | | | | | |

### 3.4 What this system does not do

- It does not rank hashtags by popularity: no counts are claimed, and a
  "broad" tag is not promised to yield more than a "niche" one on any given day.
- It does not replace account hunting. Hashtag pages surface the most viral
  texts first, which are also the most likely to already exist in the
  published history; account hunting is still where the deeper, less-reposted
  texts come from.
- It does not authorise publishing, messaging or contacting any source
  account. Hunting is read-only.
