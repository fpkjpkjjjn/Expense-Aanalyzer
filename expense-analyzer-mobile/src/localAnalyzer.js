// Полностью локальный анализатор расходов.
// Никакого Flask, Axios, IP-адреса или интернета для анализа не требуется.

const CATEGORY_KEYWORDS = {
  Groceries: [
    "pyaterochka", "magnit", "supermarket",
    "kaufland", "lidl", "billa", "tesco", "coop jednota",
    "fresh", "terno", "kraj", "koruna", "milk agro", "milk-agro",
    "potraviny", "potravina", "food store",
  ],
  Dining: [
    "cafe", "café", "restaurant", "restauracia", "reštaurácia",
    "jedlo", "pizza", "burger", "kebab", "donaska", "donáška",
    "foodora", "wolt", "bolt food", "bistro.sk", "bistro sk",
  ],
  Transport: [
    "taxi", "uber", "bolt", "dopravny podnik mesta kosice",
    "dopravný podnik mesta košice", "dpmk", "mhd", "kosice mhd",
    "elektricka", "električka", "autobus", "cestovne", "cestovné",
    "listok", "lístok", "public transport",
  ],
  Fuel: [
    "gas station", "lukoil", "slovnaft", "omv", "shell", "tanker",
    "benzin", "benzín", "nafta", "palivo", "cerpacia stanica",
    "čerpacia stanica",
  ],
  Subscriptions: [
    "spotify", "netflix", "subscription", "predplatne", "predplatné",
  ],
  Shopping: [
    "ozon", "wildberries", "purchase", "oblecenie", "oblečenie",
    "clothing", "electronic", "elektronika", "alza", "mall.sk", "mall sk",
  ],
  Health: [
    "pharmacy", "apteka", "lekaren", "lekáreň", "dm", "dm drogerie markt",
    "teta", "101 drogerie", "dr.max", "dr max", "benu", "health",
    "gym", "zdravie", "doktor", "medical",
  ],
  Entertainment: [
    "cinema", "tickets", "kino", "vstupenka", "vstupenky", "divadlo",
    "koncert", "game", "gaming",
  ],
  Housing: [
    "rent", "najom", "nájom", "housing", "byt", "hypoteka", "hypotéka",
  ],
  Utilities: [
    "electricity", "elektrina", "water", "voda", "heating", "kurenie",
    "internet", "telekom", "orange", "o2", "4ka", "vodarne", "vodárne",
    "energie", "utility", "ucet za elektrinu", "účet za elektrinu",
  ],
  Education: [
    "education", "skola", "škola", "university", "univerzita", "course",
    "kurz", "kniha", "books", "student",
  ],
  Sports: [
    "sport", "fitness", "fitko", "plavaren", "plaváreň", "stadion", "štadión",
  ],
  Travel: [
    "hotel", "booking", "airbnb", "flight", "let", "dovolenka", "travel",
    "cestovanie", "letenka", "letenky",
  ],
};

function normalize(text) {
  return String(text || "")
    .toLowerCase()
    .trim()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "");
}

const NORMALIZED_KEYWORDS = Object.fromEntries(
  Object.entries(CATEGORY_KEYWORDS).map(([category, keywords]) => [
    category,
    keywords.map(normalize),
  ])
);

function levenshtein(a, b) {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;

  const previous = Array.from({ length: b.length + 1 }, (_, i) => i);

  for (let i = 1; i <= a.length; i += 1) {
    const current = [i];
    for (let j = 1; j <= b.length; j += 1) {
      const insertion = current[j - 1] + 1;
      const deletion = previous[j] + 1;
      const substitution = previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1);
      current[j] = Math.min(insertion, deletion, substitution);
    }
    for (let j = 0; j <= b.length; j += 1) previous[j] = current[j];
  }

  return previous[b.length];
}

function similarity(a, b) {
  if (!a || !b) return 0;
  const distance = levenshtein(a, b);
  return 1 - distance / Math.max(a.length, b.length);
}

export function categorize(description) {
  const text = normalize(description);

  // Сначала точное вхождение: это наиболее предсказуемо для банковских описаний.
  for (const [category, keywords] of Object.entries(NORMALIZED_KEYWORDS)) {
    for (const keyword of keywords) {
      if (keyword && text.includes(keyword)) {
        return category;
      }
    }
  }

  // Затем мягкий fuzzy-поиск для небольших опечаток.
  let bestCategory = "Other";
  let bestScore = 0;

  for (const [category, keywords] of Object.entries(NORMALIZED_KEYWORDS)) {
    for (const keyword of keywords) {
      if (keyword.length < 5) continue;

      const score = text.includes(" ")
        ? Math.max(
            similarity(keyword, text),
            ...text.split(/\s+/).map((part) => similarity(keyword, part))
          )
        : similarity(keyword, text);

      if (score > bestScore) {
        bestScore = score;
        bestCategory = category;
      }
    }
  }

  return bestScore >= 0.88 ? bestCategory : "Other";
}

function parseDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function isoWeek(date) {
  const target = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const day = target.getUTCDay() || 7;
  target.setUTCDate(target.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(target.getUTCFullYear(), 0, 1));
  return Math.ceil(((target - yearStart) / 86400000 + 1) / 7);
}

export function analyzeTransactions(transactions) {
  const normalized = transactions.map((tx) => ({
    date: String(tx.date),
    description: String(tx.description),
    amount: Number(tx.amount),
    category: categorize(tx.description),
  }));

  const total = normalized.reduce((sum, tx) => sum + tx.amount, 0);

  const categoryTotals = {};
  normalized.forEach((tx) => {
    categoryTotals[tx.category] = (categoryTotals[tx.category] || 0) + tx.amount;
  });

  const by_category = Object.entries(categoryTotals)
    .map(([category, amount]) => ({ category, amount: round2(amount) }))
    .sort((a, b) => b.amount - a.amount);

  const weekTotals = {};
  normalized.forEach((tx) => {
    const date = parseDate(tx.date);
    if (!date) return;
    const week = isoWeek(date);
    weekTotals[week] = (weekTotals[week] || 0) + tx.amount;
  });

  const by_week = Object.entries(weekTotals)
    .map(([week, amount]) => ({ week: Number(week), amount: round2(amount) }))
    .sort((a, b) => a.week - b.week);

  const top_transactions = [...normalized]
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)
    .map((tx) => ({
      date: tx.date,
      description: tx.description,
      amount: round2(tx.amount),
      category: tx.category,
    }));

  return {
    total: round2(total),
    by_category,
    by_week,
    top_transactions,
  };
}

function round2(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}
