/**
 * Hospitality Culture Scale (HCS)
 * Dawson, M., Abbott, J., & Shoemaker, S. (2011).
 * "The Hospitality Culture Scale: A measure organizational culture and personal attributes."
 * International Journal of Hospitality Management, 30(2), 290–300.
 *
 * Três dimensões principais: Interações com Clientes, Liderança Organizacional, Clima de Trabalho.
 * Dez fatores derivados de análise de componentes principais (ACP).
 */

const LIKERT = [
  { value: 1, label: "Discordo totalmente" },
  { value: 2, label: "Discordo" },
  { value: 3, label: "Neutro" },
  { value: 4, label: "Concordo" },
  { value: 5, label: "Concordo totalmente" },
];

// ─── Seção Pessoal (atributos individuais) ────────────────────────────────────
const PERSONAL_SECTIONS = [
  {
    id: "principles",
    dimension: "Interações com Clientes",
    label: "Princípios Pessoais",
    description: "Ética, integridade e conduta no trato com pessoas.",
    color: "#2563eb",
    questions: [
      "Mantenho padrões éticos elevados em todas as minhas interações.",
      "Trato cada pessoa com respeito e equidade.",
      "Sou honesto(a) e transparente no exercício das minhas funções.",
      "Cumpro compromissos assumidos mesmo em situações adversas.",
    ],
  },
  {
    id: "propitiousness",
    dimension: "Interações com Clientes",
    label: "Propiciedade",
    description: "Adaptação do comportamento ao contexto e às pessoas.",
    color: "#7c3aed",
    questions: [
      "Adapto minha conduta conforme o perfil e as necessidades de cada cliente.",
      "Percebo sinais sociais e ajusto minha abordagem de forma adequada.",
      "Apresento-me de maneira profissional em qualquer situação.",
      "Antecipo as necessidades dos clientes antes que elas sejam expressas.",
    ],
  },
  {
    id: "leadership",
    dimension: "Liderança Organizacional",
    label: "Liderança Pessoal",
    description: "Iniciativa, influência positiva e exemplo no ambiente de trabalho.",
    color: "#0891b2",
    questions: [
      "Tomo iniciativa quando surgem problemas no trabalho.",
      "Motivo e inspiro as pessoas ao meu redor.",
      "Sirvo de exemplo positivo para meus colegas.",
      "Oriento colegas menos experientes com paciência e clareza.",
    ],
  },
  {
    id: "riskTaker",
    dimension: "Liderança Organizacional",
    label: "Disposição para Inovar",
    description: "Abertura a ideias novas e disposição para correr riscos calculados.",
    color: "#d97706",
    questions: [
      "Sinto-me confortável em propor ideias e abordagens inovadoras.",
      "Encaro mudanças e novos desafios com entusiasmo.",
      "Estou disposto(a) a correr riscos calculados para melhorar resultados.",
      "Proponho melhorias mesmo quando há resistência do ambiente.",
    ],
  },
  {
    id: "accuracy",
    dimension: "Clima de Trabalho",
    label: "Precisão e Qualidade",
    description: "Atenção a detalhes e compromisso com excelência.",
    color: "#059669",
    questions: [
      "Presto atenção cuidadosa aos detalhes do meu trabalho.",
      "Garanto que meu trabalho atenda a padrões elevados de qualidade.",
      "Verifico meu próprio trabalho para minimizar erros.",
      "Busco consistência e exatidão nas minhas entregas.",
    ],
  },
  {
    id: "composure",
    dimension: "Clima de Trabalho",
    label: "Equilíbrio Emocional",
    description: "Serenidade e profissionalismo em situações de pressão.",
    color: "#dc2626",
    questions: [
      "Mantenho a calma mesmo sob pressão intensa.",
      "Lido com situações difíceis com profissionalismo.",
      "Administro o estresse de forma eficaz no ambiente de trabalho.",
      "Ofereço soluções tranquilas mesmo diante de conflitos.",
    ],
  },
];

// ─── Seção Organizacional (cultura da empresa) ───────────────────────────────
const ORG_SECTIONS = [
  {
    id: "mgmtPrinciples",
    dimension: "Liderança Organizacional",
    label: "Princípios de Gestão",
    description: "Ética e transparência da liderança da empresa.",
    color: "#2563eb",
    questions: [
      "A gestão demonstra padrões éticos claros e consistentes.",
      "A liderança comunica-se de forma eficaz e transparente com os colaboradores.",
      "A empresa apoia ativamente o desenvolvimento profissional dos funcionários.",
      "As decisões gerenciais são justas e bem fundamentadas.",
    ],
  },
  {
    id: "customerRelationships",
    dimension: "Interações com Clientes",
    label: "Relacionamento com Clientes",
    description: "Foco e qualidade no atendimento ao cliente.",
    color: "#7c3aed",
    questions: [
      "A empresa prioriza a satisfação do cliente em todas as suas operações.",
      "Existem processos eficazes de atendimento ao cliente.",
      "A empresa coleta e age sobre o feedback dos clientes.",
      "Os funcionários são treinados para superar as expectativas dos clientes.",
    ],
  },
  {
    id: "jobVariety",
    dimension: "Clima de Trabalho",
    label: "Variedade de Funções",
    description: "Diversidade de tarefas e possibilidades de aprendizado.",
    color: "#0891b2",
    questions: [
      "Os colaboradores possuem variedade de tarefas e responsabilidades.",
      "A empresa incentiva o aprendizado em diferentes áreas.",
      "Os papéis na empresa são dinâmicos e permitem crescimento.",
      "Os funcionários têm oportunidades de atuar em projetos variados.",
    ],
  },
  {
    id: "jobSatisfaction",
    dimension: "Clima de Trabalho",
    label: "Satisfação no Trabalho",
    description: "Reconhecimento, engajamento e bem-estar dos funcionários.",
    color: "#d97706",
    questions: [
      "Os colaboradores são reconhecidos e recompensados pelo bom desempenho.",
      "A empresa promove um ambiente de trabalho positivo.",
      "Os funcionários sentem-se valorizados e engajados.",
      "Há um equilíbrio saudável entre vida pessoal e profissional.",
    ],
  },
  {
    id: "orgLeadership",
    dimension: "Liderança Organizacional",
    label: "Liderança Organizacional",
    description: "Acessibilidade, justiça e desenvolvimento promovidos pela liderança.",
    color: "#059669",
    questions: [
      "Os líderes são acessíveis e abertos ao diálogo.",
      "As decisões de liderança são transparentes e equitativas.",
      "A liderança investe ativamente no desenvolvimento de suas equipes.",
      "Os gestores servem de modelo de conduta para os colaboradores.",
    ],
  },
  {
    id: "workplaceClimate",
    dimension: "Clima de Trabalho",
    label: "Clima Organizacional",
    description: "Inclusão, colaboração e cultura positiva na empresa.",
    color: "#dc2626",
    questions: [
      "O ambiente de trabalho é inclusivo e acolhedor para todos.",
      "Os colaboradores se apoiam mutuamente e trabalham em equipe.",
      "A empresa mantém uma cultura organizacional positiva e saudável.",
      "Novos funcionários são bem recebidos e integrados com cuidado.",
    ],
  },
];

const RATING_BANDS = [
  { min: 0,  max: 20,  label: "Muito Baixo",  color: "#ef4444", emoji: "⛔" },
  { min: 20, max: 40,  label: "Baixo",         color: "#f97316", emoji: "⚠️" },
  { min: 40, max: 60,  label: "Moderado",      color: "#eab308", emoji: "🔶" },
  { min: 60, max: 80,  label: "Bom",           color: "#22c55e", emoji: "✅" },
  { min: 80, max: 101, label: "Excelente",     color: "#2563eb", emoji: "⭐" },
];

function getRating(score) {
  return RATING_BANDS.find(b => score >= b.min && score < b.max) || RATING_BANDS[RATING_BANDS.length - 1];
}

function calcScore(answers) {
  if (!answers.length) return 0;
  const sum = answers.reduce((a, b) => a + b, 0);
  return Math.round((sum / (answers.length * 5)) * 100);
}
