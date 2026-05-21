/* ─── State ──────────────────────────────────────────────────────────────────── */
const state = {
  step: 0,          // 0=intro, 1=personal questions, 2=org questions, 3=results
  personName: "",
  companyName: "",
  personalAnswers: {},  // { "sectionId-qIdx": value }
  orgAnswers: {},
  currentSectionIdx: 0,
  mode: "personal",     // "personal" | "org"
};

/* ─── Helpers ─────────────────────────────────────────────────────────────────── */
function totalSections() { return PERSONAL_SECTIONS.length + ORG_SECTIONS.length; }
function completedSections() {
  const pDone = PERSONAL_SECTIONS.filter(s =>
    s.questions.every((_, i) => state.personalAnswers[`${s.id}-${i}`] !== undefined)
  ).length;
  const oDone = ORG_SECTIONS.filter(s =>
    s.questions.every((_, i) => state.orgAnswers[`${s.id}-${i}`] !== undefined)
  ).length;
  return pDone + oDone;
}

function sectionAnswers(sections, answers, sectionId) {
  const sec = sections.find(s => s.id === sectionId);
  return sec.questions.map((_, i) => answers[`${sectionId}-${i}`]).filter(v => v !== undefined);
}

function calcSectionScore(sections, answers, sectionId) {
  return calcScore(sectionAnswers(sections, answers, sectionId));
}

function calcGroupScore(sections, answers) {
  const allVals = sections.flatMap(s =>
    s.questions.map((_, i) => answers[`${s.id}-${i}`]).filter(v => v !== undefined)
  );
  return calcScore(allVals);
}

function calcDimensionScore(sections, answers, dimensionName) {
  const allVals = sections
    .filter(s => s.dimension === dimensionName)
    .flatMap(s => s.questions.map((_, i) => answers[`${s.id}-${i}`]).filter(v => v !== undefined));
  return calcScore(allVals);
}

const DIMENSIONS = ["Interações com Clientes", "Liderança Organizacional", "Clima de Trabalho"];
const DIM_ICONS  = { "Interações com Clientes": "🤝", "Liderança Organizacional": "🏆", "Clima de Trabalho": "🌱" };

/* ─── Render helpers ──────────────────────────────────────────────────────────── */
function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  if (attrs) {
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === "class") el.className = v;
      else if (k === "style") el.style.cssText = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2).toLowerCase(), v);
      else el.setAttribute(k, v);
    });
  }
  children.flat().forEach(c => {
    if (c === null || c === undefined) return;
    el.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  });
  return el;
}

function setHTML(el, html) { el.innerHTML = html; }

/* ─── Gauge SVG ───────────────────────────────────────────────────────────────── */
function buildGauge(score, color) {
  const R = 54, cx = 60, cy = 60;
  const circ = Math.PI * R;
  const fill = circ * (score / 100);
  const dash = `${fill} ${circ}`;
  const wrap = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  wrap.setAttribute("viewBox", "6 6 108 60");
  wrap.setAttribute("width", "120");
  wrap.setAttribute("height", "64");

  const bg = document.createElementNS("http://www.w3.org/2000/svg", "path");
  bg.setAttribute("d", `M${cx - R},${cy} a${R},${R} 0 0,1 ${2*R},0`);
  bg.setAttribute("fill", "none");
  bg.setAttribute("stroke", "#e2e8f0");
  bg.setAttribute("stroke-width", "10");
  bg.setAttribute("stroke-linecap", "round");
  wrap.appendChild(bg);

  const fg = document.createElementNS("http://www.w3.org/2000/svg", "path");
  fg.setAttribute("d", `M${cx - R},${cy} a${R},${R} 0 0,1 ${2*R},0`);
  fg.setAttribute("fill", "none");
  fg.setAttribute("stroke", color);
  fg.setAttribute("stroke-width", "10");
  fg.setAttribute("stroke-linecap", "round");
  fg.setAttribute("stroke-dasharray", `0 ${circ}`);
  fg.setAttribute("stroke-dashoffset", "0");
  wrap.appendChild(fg);

  setTimeout(() => fg.setAttribute("stroke-dasharray", dash), 50);

  const scoreEl = document.createElement("div");
  scoreEl.className = "gauge-score";
  scoreEl.style.color = color;
  scoreEl.textContent = score;

  const container = document.createElement("div");
  container.className = "gauge-wrap";
  container.appendChild(wrap);
  container.appendChild(scoreEl);
  return container;
}

/* ─── STEP 0: Intro ───────────────────────────────────────────────────────────── */
function renderIntro() {
  const card = h("div", { class: "card intro-card fade-in" },
    h("div", { class: "intro-icon" }, "🏨"),
    h("h2", {}, "Avaliação de Hospitalidade"),
    h("p", {}, "Responda as perguntas a seguir para obter uma pontuação de hospitalidade baseada na Hospitality Culture Scale de Dawson, Abbott & Shoemaker (2011). A avaliação cobre atributos pessoais e cultura organizacional."),
    (() => {
      const grid = h("div", { class: "form-grid" });

      const pField = h("div", { class: "form-field" },
        h("label", {}, "Nome da Pessoa"),
        h("input", { type: "text", placeholder: "Ex.: Maria Silva", id: "inp-person", value: state.personName })
      );
      const cField = h("div", { class: "form-field" },
        h("label", {}, "Nome da Empresa"),
        h("input", { type: "text", placeholder: "Ex.: Hotel Maravilha", id: "inp-company", value: state.companyName })
      );
      grid.appendChild(pField);
      grid.appendChild(cField);

      const errMsg = h("div", { class: "error-msg hidden", id: "intro-err" }, "Preencha ambos os campos para continuar.");

      const startBtn = h("button", {
        class: "btn btn-primary btn-lg",
        onClick() {
          const pVal = document.getElementById("inp-person").value.trim();
          const cVal = document.getElementById("inp-company").value.trim();
          if (!pVal || !cVal) {
            document.getElementById("intro-err").classList.remove("hidden");
            if (!pVal) document.getElementById("inp-person").classList.add("error");
            if (!cVal) document.getElementById("inp-company").classList.add("error");
            return;
          }
          state.personName = pVal;
          state.companyName = cVal;
          state.step = 1;
          state.mode = "personal";
          state.currentSectionIdx = 0;
          render();
        }
      }, "Iniciar Avaliação →");

      return h("div", {}, grid, errMsg,
        h("div", { style: "margin-top:1.2rem" }, startBtn)
      );
    })()
  );

  return h("div", {}, card,
    h("div", { class: "footer-note" },
      h("strong", {}, "Sobre o instrumento: "),
      "A Hospitality Culture Scale (HCS) foi desenvolvida para medir a cultura organizacional da hospitalidade e atributos pessoais essenciais ao setor. Ela identifica três grandes dimensões — Interações com Clientes, Liderança Organizacional e Clima de Trabalho — além de dez fatores específicos derivados de análise de componentes principais (ACP) com 741 profissionais de hospitalidade. ",
      h("em", {}, "Dawson, M., Abbott, J., & Shoemaker, S. (2011). Int. Journal of Hospitality Management, 30(2), 290–300.")
    )
  );
}

/* ─── STEPS 1–2: Questions ───────────────────────────────────────────────────── */
function renderQuestions() {
  const isPersonal = state.mode === "personal";
  const sections = isPersonal ? PERSONAL_SECTIONS : ORG_SECTIONS;
  const answers = isPersonal ? state.personalAnswers : state.orgAnswers;
  const section = sections[state.currentSectionIdx];
  const totalSteps = PERSONAL_SECTIONS.length + ORG_SECTIONS.length;
  const globalIdx = isPersonal ? state.currentSectionIdx : PERSONAL_SECTIONS.length + state.currentSectionIdx;
  const pct = Math.round((completedSections() / totalSteps) * 100);

  function saveAnswer(secId, qIdx, val) {
    if (isPersonal) state.personalAnswers[`${secId}-${qIdx}`] = val;
    else state.orgAnswers[`${secId}-${qIdx}`] = val;
    render();
  }

  function canAdvance() {
    return section.questions.every((_, i) => answers[`${section.id}-${i}`] !== undefined);
  }

  function goNext() {
    if (!canAdvance()) return;
    if (state.currentSectionIdx < sections.length - 1) {
      state.currentSectionIdx++;
    } else if (isPersonal) {
      state.mode = "org";
      state.currentSectionIdx = 0;
    } else {
      state.step = 3;
    }
    render();
    window.scrollTo(0, 0);
  }

  function goBack() {
    if (state.currentSectionIdx > 0) {
      state.currentSectionIdx--;
    } else if (!isPersonal) {
      state.mode = "personal";
      state.currentSectionIdx = PERSONAL_SECTIONS.length - 1;
    } else {
      state.step = 0;
    }
    render();
    window.scrollTo(0, 0);
  }

  const stepBadge = isPersonal
    ? `Parte 1 de 2 · Atributos Pessoais (${state.personName})`
    : `Parte 2 de 2 · Cultura Organizacional (${state.companyName})`;

  const stepTitle = isPersonal
    ? "Avalie os atributos pessoais"
    : "Avalie a cultura da empresa";

  const stepDesc = isPersonal
    ? "Responda com base no comportamento habitual desta pessoa no ambiente de trabalho."
    : "Responda com base na sua percepção geral sobre a empresa e sua cultura.";

  // Build questions
  const qItems = section.questions.map((q, i) => {
    const current = answers[`${section.id}-${i}`];
    const likertBtns = LIKERT.map(opt =>
      h("button", {
        class: `likert-btn${current === opt.value ? " selected" : ""}`,
        onClick() { saveAnswer(section.id, i, opt.value); }
      },
        h("span", { class: "val" }, String(opt.value)),
        opt.label
      )
    );
    return h("div", { class: "question-item" },
      h("div", { class: "question-text" }, `${i + 1}. ${q}`),
      h("div", { class: "likert-row" }, ...likertBtns)
    );
  });

  const card = h("div", { class: "card fade-in" },
    h("div", { class: "section-header" },
      h("div", { class: "section-dot", style: `background:${section.color}` }),
      h("div", {},
        h("div", { class: "dim-tag" }, section.dimension),
        h("h3", {}, section.label),
        h("p", {}, section.description)
      )
    ),
    ...qItems,
    h("div", { class: "nav-row" },
      h("button", { class: "btn btn-secondary", onClick: goBack }, "← Voltar"),
      h("div", { style: "font-size:.8rem;color:var(--muted);text-align:center" },
        `${globalIdx + 1} / ${totalSteps}`
      ),
      h("button", {
        class: "btn btn-primary",
        disabled: !canAdvance() || undefined,
        onClick: goNext
      }, globalIdx + 1 === totalSteps ? "Ver Resultado →" : "Próximo →")
    )
  );

  return h("div", {},
    h("div", { class: "progress-wrap" },
      h("span", { class: "progress-label" }, "Progresso"),
      h("div", { class: "progress-bar" },
        h("div", { class: "progress-fill", style: `width:${pct}%` })
      ),
      h("span", { class: "progress-pct" }, `${pct}%`)
    ),
    h("div", { class: "step-header" },
      h("div", { class: "step-badge" }, stepBadge),
      h("h2", {}, stepTitle),
      h("p", {}, stepDesc)
    ),
    card
  );
}

/* ─── STEP 3: Results ──────────────────────────────────────────────────────────── */
function renderResults() {
  const personScore = calcGroupScore(PERSONAL_SECTIONS, state.personalAnswers);
  const companyScore = calcGroupScore(ORG_SECTIONS, state.orgAnswers);
  const pRating = getRating(personScore);
  const cRating = getRating(companyScore);

  // Per-section breakdown
  function buildBreakdown(sections, answers, title) {
    const bars = sections.map(s => {
      const sc = calcSectionScore(sections, answers, s.id);
      const rat = getRating(sc);
      return h("div", { class: "bar-item" },
        h("div", { class: "bar-top" },
          h("span", { class: "bar-label" }, s.label),
          h("span", { class: "bar-score", style: `color:${rat.color}` }, `${sc}`)
        ),
        h("div", { class: "bar-bg" },
          h("div", { class: "bar-fill", style: `width:0%;background:${s.color}`,
            // animate on next frame
          })
        ),
        h("div", { class: "bar-dim" }, s.dimension)
      );
    });

    const card = h("div", { class: "breakdown-card fade-in" },
      h("h3", {}, title),
      ...bars
    );

    // Animate bars after insertion
    setTimeout(() => {
      const fills = card.querySelectorAll(".bar-fill");
      sections.forEach((s, i) => {
        const sc = calcSectionScore(sections, answers, s.id);
        fills[i].style.width = `${sc}%`;
      });
    }, 100);

    return card;
  }

  // Dimension aggregates
  function buildDimSummary(allSections, personalA, orgA) {
    const cells = DIMENSIONS.map(dim => {
      const allSecs = [...PERSONAL_SECTIONS, ...ORG_SECTIONS].filter(s => s.dimension === dim);
      const allVals = allSecs.flatMap(s => {
        const a = PERSONAL_SECTIONS.includes(s) ? personalA : orgA;
        return s.questions.map((_, i) => a[`${s.id}-${i}`]).filter(v => v !== undefined);
      });
      const sc = calcScore(allVals);
      const rat = getRating(sc);
      return h("div", { class: "dim-cell" },
        h("div", { class: "dim-icon" }, DIM_ICONS[dim]),
        h("div", { class: "dim-name" }, dim),
        h("div", { class: "dim-score", style: `color:${rat.color}` }, `${sc}`),
        h("div", { class: "dim-rating" }, rat.label)
      );
    });

    return h("div", { class: "dim-summary fade-in" },
      h("h3", {}, "Resultado por Dimensão Principal (HCS)"),
      h("div", { class: "dim-row" }, ...cells)
    );
  }

  const el = h("div", {},
    // Score cards
    h("div", { class: "results-grid" },
      // Person
      h("div", { class: "score-card fade-in" },
        h("div", { class: "label" }, "Pessoa"),
        h("div", { class: "name" }, state.personName),
        buildGauge(personScore, pRating.color),
        h("div", { class: "rating-badge", style: `background:${pRating.color}` },
          pRating.emoji, " ", pRating.label
        ),
        h("div", { style: "font-size:.78rem;color:var(--muted);margin-top:.3rem" },
          "Atributos pessoais de hospitalidade"
        )
      ),
      // Company
      h("div", { class: "score-card fade-in" },
        h("div", { class: "label" }, "Empresa"),
        h("div", { class: "name" }, state.companyName),
        buildGauge(companyScore, cRating.color),
        h("div", { class: "rating-badge", style: `background:${cRating.color}` },
          cRating.emoji, " ", cRating.label
        ),
        h("div", { style: "font-size:.78rem;color:var(--muted);margin-top:.3rem" },
          "Cultura organizacional de hospitalidade"
        )
      )
    ),

    // Dimension summary
    buildDimSummary(
      [...PERSONAL_SECTIONS, ...ORG_SECTIONS],
      state.personalAnswers,
      state.orgAnswers
    ),

    // Breakdowns
    buildBreakdown(PERSONAL_SECTIONS, state.personalAnswers, `Fatores Pessoais — ${state.personName}`),
    buildBreakdown(ORG_SECTIONS, state.orgAnswers, `Fatores Organizacionais — ${state.companyName}`),

    // Interpretation guide
    (() => {
      const rows = RATING_BANDS.map(b =>
        `<span style="color:${b.color};font-weight:700">${b.emoji} ${b.label} (${b.min}–${b.min === 80 ? 100 : b.max})</span>`
      );
      const card = h("div", { class: "footer-note" });
      setHTML(card, `
        <strong>Interpretação da escala:</strong><br>
        ${rows.join(" &nbsp;·&nbsp; ")}<br><br>
        A pontuação é calculada a partir de uma escala Likert de 5 pontos (1 = Discordo totalmente, 5 = Concordo totalmente),
        convertida para uma escala de 0 a 100. Os dez fatores refletem os construtos identificados por Dawson, Abbott & Shoemaker (2011)
        por meio de análise de componentes principais aplicada a 741 profissionais do setor de hospitalidade.<br><br>
        <strong>Referência:</strong> Dawson, M., Abbott, J., & Shoemaker, S. (2011).
        The Hospitality Culture Scale: A measure organizational culture and personal attributes.
        <em>International Journal of Hospitality Management</em>, 30(2), 290–300.
        <a href="https://doi.org/10.1016/j.ijhm.2010.10.005" target="_blank" rel="noopener">https://doi.org/10.1016/j.ijhm.2010.10.005</a>
      `);
      return card;
    })(),

    // Restart
    h("div", { class: "restart-row" },
      h("button", {
        class: "btn btn-secondary",
        onClick() {
          state.step = 0;
          state.personalAnswers = {};
          state.orgAnswers = {};
          state.personName = "";
          state.companyName = "";
          state.currentSectionIdx = 0;
          state.mode = "personal";
          render();
          window.scrollTo(0, 0);
        }
      }, "↩ Nova Avaliação")
    )
  );

  return el;
}

/* ─── Main render ──────────────────────────────────────────────────────────────── */
function render() {
  const app = document.getElementById("app");
  app.innerHTML = "";

  const header = h("header", { class: "app-header" },
    h("h1", {}, "🏨 Avaliação de Hospitalidade"),
    h("p", { class: "subtitle" },
      "Baseado na Hospitality Culture Scale — mede atributos pessoais e cultura organizacional"
    ),
    h("span", { class: "citation" },
      "Dawson, Abbott & Shoemaker · Int. J. Hospitality Management · 2011"
    )
  );

  const container = h("div", { class: "container" });

  if (state.step === 0) container.appendChild(renderIntro());
  else if (state.step === 1 || state.step === 2) container.appendChild(renderQuestions());
  else if (state.step === 3) container.appendChild(renderResults());

  app.appendChild(header);
  app.appendChild(container);
}

/* ─── Boot ─────────────────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", render);
