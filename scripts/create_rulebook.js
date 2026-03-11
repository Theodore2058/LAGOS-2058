const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TabStopType, TabStopPosition,
} = require("docx");

// ── Constants ──
const PAGE_W = 12240, PAGE_H = 15840;
const MARGIN = 1440;
const CONTENT_W = PAGE_W - 2 * MARGIN;
const FONT = "Arial";
const C = { accent: "1B4F72", light: "D6EAF8", mid: "AED6F1", header: "2E86C1", dark: "154360", white: "FFFFFF", red: "922B21", green: "1E8449" };
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellPad = { top: 60, bottom: 60, left: 100, right: 100 };

// ── Helpers ──
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, font: FONT, size: 36, bold: true, color: C.accent })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text: t, font: FONT, size: 28, bold: true, color: C.header })] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text: t, font: FONT, size: 24, bold: true, color: C.dark })] });
const p = (t, o = {}) => new Paragraph({ spacing: { after: o.after || 120 }, alignment: o.align || AlignmentType.LEFT, children: [new TextRun({ text: t, font: FONT, size: o.size || 22, bold: o.bold, italics: o.it, color: o.color })] });
const pR = (runs, o = {}) => new Paragraph({ spacing: { after: o.after || 120 }, alignment: o.align || AlignmentType.LEFT, children: runs.map(r => new TextRun({ font: FONT, size: 22, ...r })) });
const bl = (t, ref = "bullets", lvl = 0) => new Paragraph({ numbering: { reference: ref, level: lvl }, spacing: { after: 60 }, children: [new TextRun({ text: t, font: FONT, size: 22 })] });
const blR = (runs, ref = "bullets", lvl = 0) => new Paragraph({ numbering: { reference: ref, level: lvl }, spacing: { after: 60 }, children: runs.map(r => new TextRun({ font: FONT, size: 22, ...r })) });
const ni = (t, ref) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: t, font: FONT, size: 22 })] });
const niR = (runs, ref) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60 }, children: runs.map(r => new TextRun({ font: FONT, size: 22, ...r })) });
const sp = (h = 120) => new Paragraph({ spacing: { after: h }, children: [] });
const div = () => new Paragraph({ spacing: { before: 200, after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.mid, space: 1 } }, children: [] });

function mc(children, w, o = {}) {
  const content = typeof children === "string"
    ? [new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: children, font: FONT, size: 20, bold: o.bold, color: o.fc || "000000" })] })]
    : children;
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders, margins: cellPad, shading: o.bg ? { fill: o.bg, type: ShadingType.CLEAR } : undefined, verticalAlign: "center", children: content });
}
const tr = cells => new TableRow({ children: cells });
function mt(cw, hdr, rows) {
  const tw = cw.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: cw, rows: [
    tr(hdr.map((t, i) => mc(t, cw[i], { bg: C.accent, bold: true, fc: C.white }))),
    ...rows.map((row, ri) => tr(row.map((t, i) => mc(t, cw[i], { bg: ri % 2 === 0 ? C.light : C.white })))),
  ] });
}
function callout(title, lines) {
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], rows: [
    tr([mc([
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: title, font: FONT, size: 22, bold: true, color: C.accent })] }),
      ...lines.map(l => new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: l, font: FONT, size: 20 })] })),
    ], CONTENT_W, { bg: C.light })]),
  ] });
}
// Monospace block for discord template
function codeBlock(lines) {
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], rows: [
    tr([mc(
      lines.map(l => new Paragraph({ spacing: { after: 20 }, children: [new TextRun({ text: l, font: "Courier New", size: 18, color: "333333" })] })),
      CONTENT_W, { bg: "F4F4F4" }
    )]),
  ] });
}

// ═══════════════════════════════════════════════════════
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 36, bold: true, font: FONT, color: C.accent }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: FONT, color: C.header }, paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: FONT, color: C.dark }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
    ] },
    { reference: "n1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "n2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "n3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [
    // ═══════ COVER ═══════
    {
      properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } },
      children: [
        sp(2400),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "LAGOS 2058", font: FONT, size: 72, bold: true, color: C.accent })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "POLITICAL CAMPAIGN SIMULATION", font: FONT, size: 32, color: C.header })] }),
        sp(200),
        new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 3, color: C.mid, space: 8 }, bottom: { style: BorderStyle.SINGLE, size: 3, color: C.mid, space: 8 } }, spacing: { before: 200, after: 200 }, children: [new TextRun({ text: "PLAYER RULEBOOK", font: FONT, size: 40, bold: true, color: C.dark })] }),
        sp(400),
        p("TheoStudios, RayWorks, Lincoln Productions", { align: AlignmentType.CENTER, size: 24, it: true, color: "666666", after: 40 }),
        p("In collaboration with VADELABS", { align: AlignmentType.CENTER, size: 24, it: true, color: "666666", after: 40 }),
        p("Art by TURAN", { align: AlignmentType.CENTER, size: 24, it: true, color: "666666" }),
        sp(1600),
      ],
    },
    // ═══════ BODY ═══════
    {
      properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } },
      headers: { default: new Header({ children: [new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.mid, space: 4 } }, children: [new TextRun({ text: "LAGOS 2058 Player Rulebook", font: FONT, size: 18, color: C.header, italics: true })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", font: FONT, size: 18, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "888888" })] })] }) },
      children: [
        h1("Table of Contents"),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════ 1. OVERVIEW ═══════
        h1("1. Game Overview"),
        p("LAGOS 2058 is a 12-turn political campaign simulation set in a fictional 2058 Nigeria. Players control political parties competing for electoral dominance across 774 Local Government Areas (LGAs) grouped into 8 Administrative Zones (AZs)."),
        p("Victory is determined by popular vote share and seat allocation. There are 622 seats assigned to districts proportionally to their population, allocated using the Sainte-Lagu\u00E9 method. The party with the most seats wins."),
        h2("The Spatial Voting Model"),
        p("The game uses a Merrill-Grofman spatial voting model. Every voter and every party has a position on 28 issue dimensions (ranging from -5 to +5). Voters prefer parties whose positions are close to their own. Campaign actions shift which issues voters care about, how well-known your party is, and your general appeal."),
        h2("How to Play"),
        p("Each campaign turn represents one week of real time. The cycle works as follows:"),
        ni("Plan your strategy: decide which campaign actions to take this turn, where to target them, and how to spend your Political Capital (PC).", "n1"),
        ni("Submit your actions by 12 AM EST on Friday. Include the action type, target region, and any parameters (medium, intensity, tone, etc.). The more detail you provide, the higher your quality score.", "n1"),
        ni("GMs evaluate each action for strategic fit and quality, assigning a score from 2-10 that scales the action\u2019s effectiveness.", "n1"),
        ni("The engine resolves all actions, applies effects to the campaign channels, simulates the election, and returns updated results.", "n1"),
        ni("Review your results: check vote share, seat counts, momentum, and any events (scandals, endorsement withdrawals). Plan your next turn.", "n1"),
        sp(),
        p("Repeat for 12 turns. The final simulation after Turn 12 determines the winner."),

        // ═══════ 2. TURN STRUCTURE ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("2. Turn Structure"),
        p("Each of the 12 campaign turns follows this sequence:"),
        h2("Phase 1: Start of Turn"),
        bl("Receive 7 PC base income (plus any EPO dividends)"),
        bl("Hoarding cap enforced: excess above 18 PC lost"),
        bl("Polls from previous turn delivered"),
        h2("Phase 2: Crisis Events"),
        bl("Random events may occur, applying salience shifts, valence effects, or turnout modifiers"),
        bl("Crisis Response actions can mitigate negative effects"),
        h2("Phase 3: Action Submission"),
        bl("All actions are due by 12 AM EST on Friday of each week."),
        bl("Actions are validated against your PC balance"),
        bl("Unaffordable actions are skipped"),
        h2("Phase 4: Resolution (Priority Order)"),
        p("Actions resolve in a fixed priority order by GMs over the weekend:"),
        niR([{ text: "Manifesto ", bold: true }, { text: "(positions updated first)" }], "n2"),
        niR([{ text: "EPO Engagement ", bold: true }, { text: "(institutional scores updated)" }], "n2"),
        niR([{ text: "Endorsement ", bold: true }, { text: "(coalition effects)" }], "n2"),
        niR([{ text: "Core actions ", bold: true }, { text: "(rally, advertising, media, ethnic mobilization, patronage, ground game, crisis response)" }], "n2"),
        niR([{ text: "Opposition Research ", bold: true }, { text: "(uses current exposure)" }], "n2"),
        niR([{ text: "Fundraising ", bold: true }, { text: "(generates PC for next turn)" }], "n2"),
        niR([{ text: "Intelligence ", bold: true }, { text: "(polls and EPO intel return data)" }], "n2"),
        sp(),
        h2("Phase 5: Post-Turn Updates"),
        bl("Synergy detection and bonus application"),
        bl("Fatigue counters updated"),
        bl("Election simulation run"),
        bl("Momentum tracking (rising/falling/stable vote share)"),
        bl("Scandal rolls based on exposure"),
        bl("Exposure decay (if 3+ clean turns)"),
        bl("Cohesion recovery (+1 natural, minus any hits)"),
        bl("Endorsement fragility check"),

        // ═══════ 3. PC ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("3. Political Capital (PC)"),
        p("Political Capital is the currency of campaigning. Every action costs PC. Manage it wisely."),
        h2("Income"),
        bl("Base income: 7 PC per turn (received at start of each turn)"),
        bl("EPO dividend: +1 PC if any Economic EPO score is 7 or higher (max +2/turn)"),
        bl("Fundraising: generates additional PC (see Fundraising action)"),
        h2("Hoarding Cap"),
        p("You may hold a maximum of 18 PC at the start of any turn. Excess PC above this cap is lost before income is applied. Spend it or lose it."),
        h2("No Action Limit"),
        p("There is no limit on the number of actions per turn. You may take as many actions as you can afford. Only your PC balance constrains you."),

        // ═══════ 4. ACTIONS ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("4. Campaign Actions"),
        p("There are 14 distinct action types grouped into four categories. Each action has a base PC cost, a target scope, and effects across one or more campaign channels."),

        h2("Action Cost Summary"),
        mt([2200, 1100, 1200, 1200, 3660],
          ["Action", "Cost", "Scope", "Category", "Channels Affected"],
          [
            ["Rally", "2", "District", "Outreach", "Salience, awareness, turnout, cohesion"],
            ["Advertising", "2+", "Regional", "Outreach", "Salience, awareness"],
            ["Ground Game", "3+", "District", "Outreach", "Ceiling, turnout, valence"],
            ["Media", "1", "National", "Outreach", "Valence, salience, exposure"],
            ["Endorsement", "2+", "Varies", "Political", "Valence, salience"],
            ["Patronage", "3+", "LGA", "Political", "Valence, turnout, exposure"],
            ["Ethnic Mobilization", "2", "Regional", "Political", "Salience, turnout, exposure"],
            ["EPO Engagement", "3+", "Zone", "Political", "Valence, salience, awareness"],
            ["Opposition Research", "2", "National", "Strategic", "Valence (opponent), salience"],
            ["Crisis Response", "2", "Regional", "Strategic", "Valence, awareness, cohesion"],
            ["Manifesto", "3", "National", "Strategic", "Salience, valence"],
            ["Fundraising", "2", "Varies", "Resources", "Generates PC"],
            ["Poll", "1-5", "Varies", "Resources", "Intel (next turn)"],
            ["EPO Intelligence", "0", "Zone", "Resources", "Intel (same turn)"],
          ],
        ),
        sp(),
        p("Some actions cost more when targeting larger areas or spending more for increased impact."),

        h2("Detailed Action Descriptions"),
        p("Each action description below lists the form fields you will fill out when submitting."),
        sp(),

        // ── RALLY ──
        h3("Rally (2 PC)"),
        p("A public rally in a target district. Core campaign activity and the cheapest way to rebuild cohesion."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target District, Language" }]),
        bl("Raises salience on language-profiled issue dimensions in the target district"),
        bl("Boosts awareness, scaled by population density"),
        bl("Mild turnout boost (encourages voters to show up)"),
        bl("Restores party cohesion (small but consistent)"),
        callout("LANGUAGE OPTIONS", [
          "English: tech, trade, constitutional reform",
          "Hausa: Sharia, education, traditional authority, immigration",
          "Yoruba: fiscal autonomy, resource revenue, AZ restructuring",
          "Igbo: autonomy, restructuring, trade, taxation",
          "Arabic: Sharia jurisdiction, education, traditional authority",
          "Pidgin: housing, taxation, labor, healthcare, infrastructure",
          "Mandarin: Chinese relations, trade, automation, biotech",
        ]),
        sp(),

        // ── ADVERTISING ──
        h3("Advertising (2+ PC)"),
        p("Broad messaging across one or more Administrative Zones via media channels."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target AZ(s), Language, Medium, Ad Spend" }]),
        p("Medium determines which populations you reach:"),
        bl("Radio: best reach in rural and low-media-infrastructure areas"),
        bl("TV: strong in urban, media-heavy areas (+1 PC surcharge)"),
        bl("Internet: scales with internet access; good for youth demographics"),
        p("Ad Spend determines intensity and additional effects:"),
        bl("Standard (+0 PC): baseline salience and awareness"),
        bl("Heavy (+1 PC): increased reach; also boosts turnout"),
        bl("Blitz (+2 PC): maximum impact; strongest turnout and awareness boost"),

        // ── GROUND GAME ──
        h3("Ground Game (3+ PC)"),
        p("Door-to-door canvassing and local mobilization. The strongest get-out-the-vote tool in the game."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target District, Language, Intensity" }]),
        p("Intensity tiers:"),
        bl("Standard (+0 PC): solid turnout boost, awareness from direct contact, small valence gain"),
        bl("Reinforced (+1 PC): stronger across all effects"),
        bl("Surge (+2 PC): maximum turnout impact, highest awareness and valence gains"),
        p("Ground game raises the turnout ceiling in targeted areas, meaning more voters can potentially show up. It is the primary mechanism for winning close races."),

        // ── MEDIA ──
        h3("Media (1 PC)"),
        p("The cheapest and most volatile action. Press conferences, interviews, social media blitzes."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Language, Tone, Target Party (if negative/contrast) or Narrative (if positive)" }]),
        p("Tone options:"),
        bl("Positive: highlights your own strengths; strongest own-party valence boost"),
        bl("Negative: attacks a target party; damages their valence, boosts your visibility"),
        bl("Contrast: compares your positions against a target; amplifies salience shifts"),
        p("Media impact is highly volatile: quality scores above average generate positive press, while below-average scores can backfire. Successful media blitzes also attract scrutiny, slightly increasing exposure."),

        // ── ENDORSEMENT ──
        h3("Endorsement (2+ PC)"),
        p("Secure backing from an influential figure. The endorser type determines scope and strength."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Endorser Type, Endorser Name, Target (varies by type)" }]),
        mt([2200, 1800, 5360],
          ["Endorser Type", "Scope", "Focus"],
          [
            ["Traditional Ruler", "LGA", "Traditional authority, infrastructure; strongest valence"],
            ["Religious Leader", "Regional", "Sharia, women\u2019s rights"],
            ["EPO Leader", "Regional", "Resource revenue, land tenure"],
            ["Celebrity", "National", "Bio-enhancement, media freedom; broadest reach"],
            ["Notable Figure", "District", "General issues; lowest valence impact"],
          ],
        ),
        sp(),
        callout("ENDORSEMENT FRAGILITY", [
          "30% chance endorsers withdraw if you use ethnic mobilization in the same region.",
          "Endorsers and identity politics don\u2019t mix well.",
        ]),
        sp(),

        // ── PATRONAGE ──
        h3("Patronage (3+ PC)"),
        p("Distributing resources to build local loyalty networks. High risk, high reward."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target LGA(s), Scale" }]),
        p("Scale tiers:"),
        bl("Standard (+0 PC): modest valence and turnout boost, low exposure risk"),
        bl("Heavy (+1 PC): stronger effects, moderate exposure risk"),
        bl("Massive (+2 PC): very strong valence and turnout, heavy exposure risk"),
        p("Patronage networks effectively mobilize voters but accumulate scandal risk. Higher tiers grant more valence and turnout but proportionally more exposure."),

        // ── ETHNIC MOB ──
        h3("Ethnic Mobilization (2 PC)"),
        p("Identity-targeted mobilization appealing to ethnic solidarity."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target AZ(s), Target Ethnicity" }]),
        bl("Boosts salience on identity-related dimensions (ethnic quotas, traditional authority, constitutional structure, AZ restructuring)"),
        bl("Awareness boost scaled by the target ethnic group\u2019s population share in the region"),
        bl("Moderate turnout boost among co-ethnic voters"),
        pR([{ text: "WARNING: ", bold: true, color: C.red }, { text: "Each use adds significant exposure. After roughly three uses in a campaign, scandal probability exceeds 50%." }]),

        // ── EPO ENGAGEMENT ──
        h3("EPO Engagement (3+ PC)"),
        p("Build institutional support with Extra-Party Organizations in a zone. A long-term investment that pays dividends."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target AZ, Category, Score Change (1-5)" }]),
        p("EPO categories and what they influence:"),
        bl("Economic: resource revenue, land tenure, taxation"),
        bl("Labor: labor automation, education"),
        bl("Elite: Chinese relations, constitutional structure"),
        bl("Youth: biotech, media freedom, environment"),
        p("Your EPO score in each zone ranges from 0 to 10. Each engagement attempt raises it by the Score Change amount (scaled by quality). Requesting a score change above 3 costs +1 PC."),
        callout("LONG-TERM INVESTMENT", [
          "EPO pays off over time: scores of 7+ grant +1 PC/turn dividend.",
          "Scores of 5+ unlock free EPO Intelligence actions.",
          "Parties that ignore EPO suffer PC shortages in turns 9-12.",
        ]),
        sp(),

        // ── OPPOSITION RESEARCH ──
        h3("Opposition Research (2 PC)"),
        p("Investigate and publicize an opponent\u2019s weaknesses."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target Party, Target Dimensions (up to 4, or leave blank for auto-detect)" }]),
        bl("Raises salience on the chosen dimensions (ideally ones where the target party is weak)"),
        bl("Damages the target party\u2019s valence (reputation hit)"),
        bl("Minor awareness boost for your party (you\u2019re in the news)"),
        bl("Costs cohesion: going negative is internally controversial"),

        // ── CRISIS RESPONSE ──
        h3("Crisis Response (2 PC)"),
        p("React to negative events to protect your reputation. Best used when a crisis event hits your region."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target AZ(s)" }]),
        bl("Protects and boosts your valence (demonstrates competence)"),
        bl("High visibility awareness boost"),
        bl("Significant cohesion boost (rallying around the crisis strengthens the party)"),
        bl("Exempt from action fatigue"),

        // ── MANIFESTO ──
        h3("Manifesto (3 PC)"),
        p("A major national policy statement that repositions your party on the 28 issue dimensions."),
        pR([{ text: "Form fields: ", bold: true }, { text: "New positions on each of the 28 dimensions (-5 to +5)" }]),
        bl("REQUIRED by week three of the game"),
        bl("Updates your party\u2019s position vector across all 28 dimensions"),
        bl("Raises awareness nationally (proportional to media infrastructure)"),
        bl("May be done more than once if a party wishes to dramatically realign itself"),
        pR([{ text: "WARNING: ", bold: true, color: C.red }, { text: "Sharp reversals (>3-point shift on any single dimension) trigger a credibility penalty to valence and a cohesion hit of -1 to -3." }]),

        // ── FUNDRAISING ──
        h3("Fundraising (2 PC)"),
        p("Spend 2 PC upfront to generate more PC. Source determines yield and side effects."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Source" }]),
        mt([2000, 2000, 5360],
          ["Source", "Base Yield", "Side Effects"],
          [
            ["Diaspora", "4 PC", "None (safe default)"],
            ["Business Elite", "5 PC", "Heavy exposure risk"],
            ["Grassroots", "4 PC", "Turnout and awareness boost in target region"],
            ["Membership", "2-5 PC (scales with cohesion)", "Cohesion recovery"],
          ],
        ),
        sp(),
        bl("Using the same source repeatedly reduces yield by -1 PC per consecutive repeat"),
        bl("Economic EPO scores of 7+ grant +1 PC bonus to any fundraising"),
        bl("Final yield is scaled by your GM quality score: poor quality can result in net loss"),

        // ── POLL ──
        h3("Poll (1-5 PC)"),
        p("Commission polling to gather intelligence on voter issue positions."),
        pR([{ text: "Form fields: ", bold: true }, { text: "Poll Tier" }]),
        mt([1500, 1500, 3180, 3180],
          ["Tier", "Cost", "Scope", "Margin of Error"],
          [
            ["1", "1 PC", "LGA", "+/- 1"],
            ["2", "2 PC", "District", "+/- 2"],
            ["3", "3 PC", "State", "+/- 3"],
            ["4", "4 PC", "Zone", "+/- 4"],
            ["5", "5 PC", "National Aggregate", "+/- 5"],
          ],
        ),
        sp(),
        pR([{ text: "Important: ", bold: true }, { text: "Poll results are delivered next turn, not immediately. Polls are exempt from GM quality scoring." }]),

        // ── EPO INTELLIGENCE ──
        h3("EPO Intelligence (0 PC)"),
        pR([{ text: "FREE ", bold: true, color: C.green }, { text: "zone-level voter position data. Requires EPO score of 5 or higher in the target zone." }]),
        pR([{ text: "Form fields: ", bold: true }, { text: "Target AZ" }]),
        bl("Delivered same turn (unlike polls)"),
        bl("Precision improves with higher EPO scores"),
        bl("Exempt from GM quality scoring"),

        // ═══════ 5. CHANNELS ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("5. The Five Campaign Channels"),
        p("Every campaign action operates through one or more of these five channels. Understanding them is key to effective strategy."),
        h2("5.1 Awareness"),
        p("How well-known your party is in each LGA. Ranges from 0.60 (floor) to 1.0 (cap)."),
        bl("Awareness can only go up, it will never go down"),
        bl("Higher awareness means voters are more aware of what your party\u2019s positions actually are"),
        bl("Most actions contribute some awareness boost"),
        bl("Scales multiplicatively with voter utility"),
        h2("5.2 Salience (Issue Emphasis)"),
        p("How much voters in a region care about each of the 28 issue dimensions."),
        bl("Base salience varies by LGA (regional and ethnic factors)"),
        bl("Campaign actions shift salience additively"),
        h2("5.3 Valence (Party Appeal)"),
        p("General party attractiveness independent of ideology. Think of it as likability or trustworthiness."),
        bl("Boosted by: endorsements, ground game, positive media, crisis response"),
        bl("Damaged by: opposition research (from opponents), scandals, manifesto reversals, high exposure"),
        bl("Directly added to voter utility calculation"),
        h2("5.4 Turnout Ceiling"),
        p("The maximum turnout achievable in an LGA, acting as a soft cap above the baseline."),
        bl("Ground game and heavy advertising raise the ceiling"),
        bl("Interacts with abstention modifier to determine final turnout"),
        h2("5.5 Turnout Modifier"),
        p("Adjusts voter abstention. Actions ranked by turnout impact, strongest to weakest:"),
        mt([4000, 2680, 2680],
          ["Action", "Turnout Impact", "Notes"],
          [
            ["Ground Game (Surge)", "Very strong", "Strongest GOTV tool in the game"],
            ["Patronage (Massive)", "Strong", "Effective but carries heavy exposure"],
            ["Ground Game (Standard)", "Moderate-strong", "Reliable and clean"],
            ["Patronage (Standard)", "Moderate", "Lower exposure than heavy"],
            ["Ethnic Mobilization", "Moderate", "Identity-driven turnout; adds exposure"],
            ["Rally", "Mild", "Cheap, steady turnout nudge"],
            ["Advertising (Heavy/Blitz)", "Mild", "Only with budget 1+"],
          ],
        ),
        sp(),
        callout("TURNOUT MATTERS", [
          "In close races, turnout decides seats. Ground game is the primary turnout driver.",
          "Patronage also drives turnout effectively, but carries exposure risk.",
          "A party with great policy positions but low turnout will lose to a weaker party that gets voters to the polls.",
        ]),
        sp(),

        // ═══════ 6. COHESION ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("6. Party Cohesion"),
        p("Cohesion represents your party\u2019s internal unity on a scale of 0 to 10. All parties start at 10 (perfect unity). Lower cohesion weakens every campaign action."),
        h2("Cohesion Multiplier"),
        p("Your cohesion level determines an effectiveness multiplier applied to all campaign effects:"),
        mt([2340, 2340, 2340, 2340],
          ["Cohesion", "Multiplier", "Effectiveness", "Status"],
          [["8-10", "1.00x", "Full", "Healthy"], ["6-8", "0.70-1.00x", "Reduced", "Strained"], ["4-6", "0.40-0.70x", "Weak", "Fractured"], ["2-4", "0.15-0.40x", "Crippled", "Crisis"], ["0-2", "0.15x", "Minimal", "Collapsed"]],
        ),
        sp(),
        h2("What Affects Cohesion"),
        mt([4680, 4680], ["Event", "Effect"],
          [["Rally", "Small boost"], ["Crisis Response", "Significant boost"], ["Membership Fundraising", "Small boost"], ["Broad Engagement (3+ AZs in one turn)", "+1.0"], ["Natural Recovery (per turn)", "+1.0"], ["Manifesto Reversal (>3pt shift)", "-1 to -3"], ["Opposition Research", "Small penalty"], ["Scandal", "-1.0"], ["Region Neglect (3+ turns)", "-1.0"]],
        ),
        sp(),
        h2("Regional Engagement"),
        bl("The game tracks which AZs you campaign in each turn"),
        bl("Neglect penalty: if your support base AZ is not engaged for 3+ consecutive turns, you lose cohesion"),
        bl("Engagement bonus: campaigning in 3+ distinct AZs in a single turn grants +1.0 cohesion"),

        // ═══════ 7. EXPOSURE ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("7. Exposure and Scandals"),
        p("Exposure is cumulative reputational risk from controversial actions. Too much exposure triggers scandals."),
        h2("Exposure Sources"),
        mt([4000, 2680, 2680], ["Action", "Exposure Added", "Risk Level"],
          [["Ethnic Mobilization", "+0.8 per use", "High"], ["Patronage (Standard / Heavy / Massive)", "+0.3 / +0.6 / +0.9", "Medium-High"], ["Business Elite Fundraising", "+1.5", "Very High"], ["Successful Media", "Small amount", "Low"]],
        ),
        sp(),
        h2("Scandal Probability"),
        p("Each turn, the game rolls for scandal based on your current exposure:"),
        mt([3120, 3120, 3120], ["Exposure", "Scandal Chance", "Risk Assessment"],
          [["0.0 - 2.0", "0%", "Safe"], ["2.0 - 3.0", "5%", "Low risk"], ["3.0 - 4.0", "15%", "Moderate"], ["4.0 - 6.0", "30%", "Dangerous"], ["6.0 - 9.0", "50%", "Very dangerous"], ["9.0+", "75%", "Near-certain"]],
        ),
        sp(),
        h2("Scandal Consequences"),
        p("When a scandal triggers, your party suffers:"),
        bl("Valence penalty"), bl("PC damage: -3 PC"), bl("Cohesion hit: -1.0"), bl("Exposure halved (partial reputation recovery after the fallout)"),
        h2("Exposure Decay"),
        bl("After 3 consecutive clean turns (no new exposure), exposure decays by -1.0 per turn"),
        bl("Ongoing penalty: negative valence per point of exposure above 1.0"),
        callout("RISK MANAGEMENT", ["Front-load risky actions (ethnic mobilization, patronage) early in the campaign.", "After turn 6, switch to clean actions to let exposure decay.", "A late-game scandal is devastating: PC loss + valence hit + cohesion damage all at once."]),
        sp(),

        // ═══════ 8. QUALITY ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("8. Action Quality (GM Scoring)"),
        p("Every action receives a quality score from the Game Master that determines its effectiveness. Higher quality means stronger effects."),
        h2("Score Components"),
        p("GM Score = Strategic Fit (1-5) + Quality (1-5), giving a range of 2-10."),
        blR([{ text: "Strategic Fit (1-5): ", bold: true }, { text: "Is this the right action for the right region, demographic, issue, and language?" }]),
        blR([{ text: "Quality (1-5): ", bold: true }, { text: "How detailed, realistic, and contextually aware is the action?" }]),
        h2("Creativity Bonuses"),
        p("Each of the following adds +1 to quality (capped at 5 total):"),
        bl("Providing actual speech content, ad copy, or narrative"),
        bl("Describing visual or audio production elements"),
        bl("Including strategic documentation or rationale"),
        h2("Score Multiplier"),
        mt([2340, 2340, 2340, 2340], ["Score", "Multiplier", "Label", "Impact"],
          [["2", "0.33x", "Poor", "Action mostly fails"], ["4", "0.67x", "Below Average", "Reduced impact"], ["6", "1.00x", "Average", "Normal impact"], ["8", "1.33x", "Good", "Enhanced impact"], ["10", "1.67x", "Excellent", "Maximum impact"]],
        ),
        sp(),
        h2("Additional Modifiers"),
        bl("EPO Interaction: +1 if any EPO score is 7+"), bl("Momentum: +0.5 per momentum level"), bl("Low Cohesion: -1 if cohesion is between 4-5"), bl("Media Volatility: 2x deviation from score 5 (amplifies both good and bad)"),
        pR([{ text: "Note: ", bold: true }, { text: "Poll and EPO Intelligence actions always use a 1.0x multiplier regardless of quality." }]),

        // ═══════ 9. DIMINISHING RETURNS ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("9. Diminishing Returns"),
        h2("Action Fatigue"),
        p("Repeating the same action type across consecutive turns yields diminishing returns."),
        mt([3120, 3120, 3120], ["Consecutive Turns", "Multiplier", "Effectiveness Loss"],
          [["1 (first use)", "1.00x", "None"], ["2", "0.83x", "-17%"], ["3", "0.71x", "-29%"], ["4", "0.63x", "-37%"], ["5", "0.56x", "-44%"]],
        ),
        sp(),
        bl("Skip a turn to reset the fatigue counter for that action type"),
        blR([{ text: "Exempt actions: ", bold: true }, { text: "Fundraising, Poll, Manifesto, and Crisis Response are not subject to fatigue" }]),
        h2("Concentration Penalty"),
        p("Targeting the same geographic region repeatedly also sees reduced effectiveness."),
        mt([3120, 3120, 3120], ["Consecutive Turns in Region", "Multiplier", "Effectiveness Loss"],
          [["1 (first use)", "1.00x", "None"], ["2", "0.87x", "-13%"], ["3", "0.77x", "-23%"], ["4", "0.69x", "-31%"]],
        ),
        sp(),
        bl("Switch to a different region to reset the counter"),

        // ═══════ 10. SYNERGIES ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("10. Action Synergies"),
        p("Pairing complementary actions in the same turn on overlapping regions generates bonus effects."),
        mt([3120, 3120, 3120], ["Action 1", "Action 2", "Bonus Channel"],
          [["Rally", "Ground Game", "Valence"], ["Advertising", "Rally", "Salience"], ["Media", "Opposition Research", "Opponent Valence"], ["Endorsement", "Rally", "Valence"], ["Patronage", "Ground Game", "Turnout"]],
        ),
        sp(),
        h2("Synergy Conditions"),
        bl("Overlapping target regions (national actions overlap with any region)"),
        bl("Only the specific pairs listed above trigger synergies"),
        callout("STRATEGIC TIP", ["Synergies reward concentrated effort. A Rally + Ground Game + Endorsement in one district", "triggers two synergy bonuses and is far more effective than spreading those actions across three regions."]),
        sp(),

        // ═══════ 11. ELECTION ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("11. How Votes Are Calculated"),
        p("At the end of each turn, the election engine simulates the outcome based on current campaign modifiers."),
        h2("Voter Utility"),
        p("Each voter calculates a utility score for every party based on:"),
        niR([{ text: "Spatial proximity", bold: true }, { text: " \u2014 how close is the party to the voter\u2019s ideal position on salient issues?" }], "n3"),
        niR([{ text: "Ethnic affinity", bold: true }, { text: " \u2014 does the party leader share the voter\u2019s ethnicity?" }], "n3"),
        niR([{ text: "Religious affinity", bold: true }, { text: " \u2014 does the party align with the voter\u2019s religion?" }], "n3"),
        niR([{ text: "Valence", bold: true }, { text: " \u2014 general party appeal and trustworthiness" }], "n3"),
        niR([{ text: "Awareness", bold: true }, { text: " \u2014 how well-known is the party in this area?" }], "n3"),
        sp(),
        h2("Turnout"),
        p("Voters also consider abstaining. A virtual \u2018abstention option\u2019 competes with parties. Factors making voters more likely to abstain:"),
        bl("Alienation: no party is close to the voter\u2019s ideal position"),
        bl("Indifference: multiple parties are equally appealing (no clear choice)"),
        bl("Demographic factors: youth, unemployment, and lower education increase abstention"),
        p("Factors making voters more likely to vote:"),
        bl("Tertiary education, older age, urban location, public sector employment"),
        bl("Campaign effects: ground game, rally, patronage all reduce abstention"),
        h2("Seat Allocation"),
        bl("Each voting district awards seats to parties using the Sainte-Lagu\u00E9 method."),
        bl("There are 622 seats assigned to districts proportionally to their population"),

        // ═══════ 12. DIMENSIONS ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("12. The 28 Issue Dimensions"),
        p("Every party and voter has a position on each dimension, ranging from -5 to +5. The labels below describe the poles of each spectrum."),
        sp(),
        mt([600, 2500, 6260], ["#", "Dimension", "Spectrum"],
          [
            ["1", "Sharia jurisdiction", "Fully secular legal system \u2194 full Sharia implementation"],
            ["2", "Fiscal autonomy", "Strong federal centralism \u2194 confederal fiscal independence"],
            ["3", "Chinese relations", "Western-aligned foreign policy \u2194 deepened WAFTA partnership"],
            ["4", "BIC reform", "Abolish the BIC institution \u2194 preserve and strengthen it"],
            ["5", "Ethnic quotas", "Pure meritocracy in hiring \u2194 affirmative action / quota systems"],
            ["6", "Resource revenue", "Federal control of resource wealth \u2194 producing-state ownership"],
            ["7", "Constitutional structure", "Unitary centralized government \u2194 devolved regional power"],
            ["8", "AZ restructuring", "Keep current AZ boundaries \u2194 redraw along ethnic/economic lines"],
            ["9", "Traditional authority", "Ceremonial role for traditional rulers \u2194 formal governing power"],
            ["10", "Women\u2019s rights", "Traditional gender norms \u2194 full legal gender equality"],
            ["11", "Fertility policy", "No state involvement in family size \u2194 active population control"],
            ["12", "Education", "Privatized / religious education \u2194 secular universal public education"],
            ["13", "Infrastructure", "Private-led development \u2194 large-scale state infrastructure programs"],
            ["14", "Security", "Community / traditional policing \u2194 centralized federal security forces"],
            ["15", "Land tenure", "Customary / communal ownership \u2194 formalized private title system"],
            ["16", "Language policy", "Promote indigenous languages \u2194 English-only national standard"],
            ["17", "Biological enhancement", "Ban genetic / biotech modification \u2194 embrace human augmentation"],
            ["18", "Media freedom", "State-regulated media \u2194 unrestricted press and digital speech"],
            ["19", "Pada status", "Full integration of Pada into society \u2194 restricted Pada rights"],
            ["20", "Healthcare", "Private market healthcare \u2194 universal public health system"],
            ["21", "Housing", "Market-driven housing \u2194 state-funded mass housing programs"],
            ["22", "Taxation", "Minimal taxation / flat tax \u2194 progressive taxation with redistribution"],
            ["23", "Labor automation", "Unrestricted AI and automation \u2194 worker-protection regulations"],
            ["24", "Trade policy", "Free trade / open borders \u2194 protectionist domestic industry policy"],
            ["25", "Climate adaptation", "Market-led climate response \u2194 state-mandated green transition"],
            ["26", "Water infrastructure", "Local / private water systems \u2194 national public water grid"],
            ["27", "Immigration", "Open immigration policy \u2194 strict border controls"],
            ["28", "Digital governance", "Minimal digital regulation \u2194 comprehensive digital ID / e-gov"],
          ],
        ),
        sp(),

        // ═══════ 13. QUICK REF ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("13. Quick Reference"),
        h2("Action Efficiency Ranking"),
        mt([2000, 1200, 2200, 3960], ["Action", "Cost", "Best For", "Watch Out For"],
          [["Media", "1 PC", "Cheap broad impact", "High variance"], ["Rally", "2 PC", "Salience + cohesion", "Fatigue if repeated"], ["Fundraising", "2 PC", "PC generation", "Source penalties if repeated"], ["Ground Game", "3+ PC", "Turnout (strongest)", "Expensive at higher tiers"], ["Endorsement", "2+ PC", "Valence boost", "Fragility with ethnic mob"], ["Patronage", "3+ PC", "Loyalty + turnout", "Heavy exposure risk"]],
        ),
        sp(),
        h2("Critical Warnings"),
        callout("DO NOT", ["Hoard PC above 18 (excess is lost each turn)", "Use sharp manifesto shifts of >3 points (credibility + cohesion penalty)", "Spam ethnic mobilization (3+ uses = 50%+ scandal chance)", "Repeat the same action 3+ turns in a row (25%+ effectiveness loss)", "Ignore your home base AZ for 3+ turns (cohesion penalty)", "Neglect EPO early game (you\u2019ll lack income and intel late game)"]),
        sp(),

        // ═══════ 14. DISCORD TEMPLATE ═══════
        new Paragraph({ children: [new PageBreak()] }),
        h1("14. Action Submission Template"),
        p("Copy the template below into Discord to submit your actions each turn. Include one block per action. The more detail you provide in the Description field, the higher your GM quality score."),
        sp(),
        codeBlock([
          "## TURN [#] \u2014 [Party Name]",
          "Current PC: [amount]",
          "",
          "### Action 1",
          "Type: [see list below]",
          "Target: [district / AZ(s) / LGA(s) / national]",
          "",
          "--- Parameters (include only what applies) ---",
          "Language: [english / hausa / yoruba / igbo / arabic",
          "           / pidgin / mandarin]",
          "  (rally, advertising, ground_game, media)",
          "",
          "Medium: [radio / tv / internet]  (advertising)",
          "Ad Spend: [standard / heavy / blitz]  (advertising)",
          "Intensity: [standard / reinforced / surge]  (ground_game)",
          "Scale: [standard / heavy / massive]  (patronage)",
          "Tone: [positive / negative / contrast]  (media)",
          "Narrative: [text]  (media, positive tone)",
          "Target Party: [name]  (oppo research, negative/contrast media)",
          "Target Dims: [up to 4 issue names]  (oppo research)",
          "Endorser Type: [traditional_ruler / religious_leader",
          "   / epo_leader / celebrity / notable]  (endorsement)",
          "Endorser Name: [name]  (endorsement)",
          "EPO Category: [economic / labor / elite / youth]  (epo_engagement)",
          "Score Change: [1-5]  (epo_engagement)",
          "Source: [diaspora / business_elite / grassroots",
          "         / membership]  (fundraising)",
          "Poll Tier: [1-5]  (poll)",
          "",
          "Description:",
          "[Describe what your party is doing. Include speech",
          " content, ad copy, strategic rationale, or production",
          " details for creativity bonuses.]",
          "",
          "### Action 2",
          "Type: ...",
          "(repeat as needed)",
        ]),
        sp(),
        h2("Action Types Quick List"),
        mt([2340, 2340, 4680], ["Type", "Base Cost", "Required Parameters"],
          [
            ["rally", "2 PC", "Target District, Language"],
            ["advertising", "2+ PC", "Target AZ(s), Language, Medium, Ad Spend"],
            ["ground_game", "3+ PC", "Target District, Language, Intensity"],
            ["media", "1 PC", "Language, Tone, Target Party or Narrative"],
            ["endorsement", "2+ PC", "Endorser Type, Endorser Name, Target"],
            ["patronage", "3+ PC", "Target LGA(s), Scale"],
            ["ethnic_mobilization", "2 PC", "Target AZ(s), Target Ethnicity"],
            ["epo_engagement", "3+ PC", "Target AZ, EPO Category, Score Change"],
            ["opposition_research", "2 PC", "Target Party, Target Dims (optional)"],
            ["crisis_response", "2 PC", "Target AZ(s)"],
            ["manifesto", "3 PC", "New positions (28 dimensions)"],
            ["fundraising", "2 PC", "Source"],
            ["poll", "1-5 PC", "Poll Tier"],
            ["epo_intelligence", "0 PC", "Target AZ (requires EPO 5+)"],
          ],
        ),
        sp(),
        sp(),
        div(),
        p("End of Rulebook", { align: AlignmentType.CENTER, it: true, color: "888888", size: 20 }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("C:/Default/LAGOS-2058/LAGOS_2058_Player_Rulebook.docx", buf);
  console.log("Rulebook created: LAGOS_2058_Player_Rulebook.docx");
});
