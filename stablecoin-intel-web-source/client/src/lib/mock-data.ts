export interface NewsItem {
  id: string;
  title: string;
  source: string;
  date: string;
  url: string;
  threatLevel: 'high' | 'medium' | 'low' | 'neutral';
  category: 'competitor' | 'customer' | 'industry';
  summary: string;
  impact: string[];
  action: string;
  tickers?: string[];
}

export const mockNews: NewsItem[] = [
  {
    id: '1',
    title: "Fidelity to Enter Stablecoin Market With Ethereum-Based 'Digital Dollar'",
    source: "Decrypt",
    date: "2026-01-29",
    url: "https://decrypt.co/356165/fidelity-enters-stablecoin-market-ethereum-digital-dollar",
    threatLevel: 'high',
    category: 'competitor',
    summary: "富达将推出基于以太坊的稳定币，进入稳定币市场。这一举动标志着传统金融巨头正式通过公链进入稳定币领域，可能对现有的USDC/USDT双寡头格局造成冲击。",
    impact: ["产品竞争", "市场定价", "品牌影响"],
    action: "密切关注富达的市场动向，调整产品策略。分析其合规架构与DeFi集成方案。",
    tickers: ["ETH", "USD"]
  },
  {
    id: '2',
    title: "Checkout.com acquires euro stablecoin issuer Blue EMI",
    source: "Finextra Research",
    date: "2026-01-29",
    url: "#",
    threatLevel: 'medium',
    category: 'competitor',
    summary: "Checkout.com收购了欧元稳定币发行商Blue EMI，可能对市场竞争格局产生影响。支付巨头垂直整合稳定币发行能力，将降低其支付成本并提高结算效率。",
    impact: ["市场定价", "客户争夺", "品牌影响"],
    action: "关注Checkout.com的市场策略变化，评估潜在影响。特别是其在欧洲市场的商户拓展情况。",
    tickers: ["EUR"]
  },
  {
    id: '3',
    title: "Cactus Custody Pushes MPC Self-Custody – Full Control, But Compliance",
    source: "Twitter @CNews_Hub",
    date: "2026-01-29",
    url: "#",
    threatLevel: 'medium',
    category: 'competitor',
    summary: "Cactus Custody推出了MPC自我托管平台，强调合规性的重要性。这种混合模式试图解决机构对完全自托管的安全顾虑与合规要求。",
    impact: ["技术差距", "合规优势"],
    action: "关注Cactus Custody的合规策略，评估其对市场的影响。对比我们的MPC方案优势。",
  },
  {
    id: '4',
    title: "Mizuho upgrades Circle shares outlook citing Polymarket’s use of USDC",
    source: "The Block",
    date: "2026-01-29",
    url: "#",
    threatLevel: 'low',
    category: 'customer',
    summary: "Mizuho 将 Circle 的股票评级上调至“中性”，并提高目标股价至77美元。Polymarket的高频小额结算场景证明了USDC在预测市场中的实用性。",
    impact: ["客户扩展"],
    action: "关注 Polymarket 使用 USDC 的动态，寻找潜在合作机会。",
    tickers: ["USDC"]
  },
  {
    id: '5',
    title: "Gemini Launches Zcash Credit Card That Pays ZEC Rewards",
    source: "Decrypt",
    date: "2026-01-29",
    url: "#",
    threatLevel: 'neutral',
    category: 'customer',
    summary: "Gemini推出了一款以Zcash为主题的信用卡，持卡人可获得ZEC奖励。这是隐私币与传统支付网络结合的尝试。",
    impact: ["客户扩展", "市场拓展"],
    action: "考虑与Gemini合作，探索ZEC奖励的潜在市场机会。",
    tickers: ["ZEC"]
  },
  {
    id: '6',
    title: "SEC clarifies rules for tokenized securities",
    source: "The Block",
    date: "2026-01-29",
    url: "#",
    threatLevel: 'high',
    category: 'industry',
    summary: "SEC明确了代币化证券的规则，将其纳入联邦证券法的监管范围。这将增加RWA（现实世界资产）项目的合规成本，但同时也提供了明确的法律路径。",
    impact: ["监管影响", "市场趋势"],
    action: "关注监管动态以调整合规策略。审查现有代币化资产的法律结构。",
  },
  {
    id: '7',
    title: "TrustLinq 提供将稳定币转化为法币支付的服务",
    source: "Twitter @Trustlinq",
    date: "2026-01-28",
    url: "#",
    threatLevel: 'medium',
    category: 'competitor',
    summary: "TrustLinq 提供将稳定币转化为法币支付的服务，可能对我们的市场份额造成影响。其声称实现了T+0结算。",
    impact: ["产品竞争", "客户争夺"],
    action: "考虑优化我们的支付基础设施和合规策略，以提升竞争力。",
  },
  {
    id: '8',
    title: "Tether推出受美国监管的USAT稳定币",
    source: "Twitter @DynamoDeFi",
    date: "2026-01-28",
    url: "#",
    threatLevel: 'neutral',
    category: 'industry',
    summary: "Tether推出受美国监管的USAT稳定币，反映出稳定币市场的监管趋势和创新。这可能是Tether试图摆脱监管困境的重要一步。",
    impact: ["市场趋势"],
    action: "监测USAT的市场接受度和流动性增长情况。",
    tickers: ["USAT", "USDT"]
  }
];

export const stats = {
  totalThreats: 12,
  highThreats: 3,
  mediumThreats: 5,
  lowThreats: 4,
  competitorUpdates: 11,
  customerUpdates: 4,
  industryUpdates: 48
};

export const dailySummary = {
  competitorThreat: "今日最大的竞争威胁来自富达（Fidelity），其即将推出的以太坊基础稳定币“数字美元”可能会显著改变市场格局。此外，Checkout.com收购欧元稳定币发行商Blue EMI，进一步加剧了市场竞争。Cactus Custody推出了多项自托管平台，强调合规性，增强了其市场地位。",
  industryTrend: "今日行业热点集中在SEC对代币化证券的监管明确性、Fidelity即将推出的美元支持稳定币FIDD，以及Crypto PAC Fairshake在政治领域的影响力。SEC将代币化资产视为证券，强调投资者保护，这可能促使市场对合规稳定币的需求上升。"
};

export interface ReportSummary {
  id: string;
  date: string;
  title: string;
  summary: string;
  stats: {
    high: number;
    medium: number;
    low: number;
    /** 竞争对手更新总数，与详情页/API 对齐；无则用 medium+low */
    competitorUpdates?: number;
  };
  type: 'daily' | 'weekly';
}

// 仅保留 01-28、01-29 日报，与 docs/daily-reports.js 一致
export const reportList: ReportSummary[] = [
  {
    id: '2026-01-29',
    date: '2026-01-29',
    title: 'Daily Intelligence Brief',
    summary: 'Fidelity enters stablecoin market; Checkout.com acquires Blue EMI.',
    stats: { high: 3, medium: 5, low: 4 },
    type: 'daily'
  },
  {
    id: '2026-01-28',
    date: '2026-01-28',
    title: 'Daily Intelligence Brief',
    summary: 'TrustLinq launches fiat ramp; Tether releases USAT.',
    stats: { high: 1, medium: 3, low: 2 },
    type: 'daily'
  },
  {
    id: 'w-2026-04',
    date: '2026-01-26',
    title: 'Weekly Market Overview (Week 4)',
    summary: 'Comprehensive analysis of Week 4 trends: Institutional adoption rising.',
    stats: { high: 5, medium: 12, low: 15 },
    type: 'weekly'
  },
  {
    id: 'w-2026-03',
    date: '2026-01-19',
    title: 'Weekly Market Overview (Week 3)',
    summary: 'Regulatory clarity improves in EU; APAC region shows growth.',
    stats: { high: 2, medium: 8, low: 10 },
    type: 'weekly'
  }
];
