import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

/* ══════════════════════════════════════════════════════════════
   CHENGETA AI — brand palette
   Forest Green #0F5B3A · Deep Emerald #1B7F5A · Gold #C9A227
   Black #111111 · White #FFFFFF · Light Sand #F7F3E8
══════════════════════════════════════════════════════════════ */
const C = {
  bg: '#0B140F',
  panel: '#10211A',
  panelAlt: '#0E1C15',
  border: '#1C3B2C',
  green: '#0F5B3A',
  emerald: '#1B7F5A',
  emeraldBright: '#3DBF86',
  gold: '#C9A227',
  goldSoft: 'rgba(201,162,39,0.12)',
  sand: '#F7F3E8',
  text: '#EAF2EC',
  muted: '#9DB3A6',
  faint: '#6E867A',
};
const GRADIENT = `linear-gradient(135deg, ${C.emeraldBright}, ${C.gold})`;

function GradientText({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        background: GRADIENT,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}
    >
      {children}
    </span>
  );
}

function Divider() {
  return (
    <div
      style={{
        height: 1,
        background: `linear-gradient(to right, transparent, ${C.border}, transparent)`,
        margin: '4rem 0',
      }}
    />
  );
}

/* Geometric African-inspired chevron band — subtle brand texture */
function ChevronBand() {
  return (
    <svg width="100%" height="14" viewBox="0 0 240 14" preserveAspectRatio="none" aria-hidden="true" style={{ display: 'block', opacity: 0.5 }}>
      <defs>
        <pattern id="chev" width="24" height="14" patternUnits="userSpaceOnUse">
          <path d="M0 14 L12 2 L24 14" fill="none" stroke={C.gold} strokeWidth="1.4" />
        </pattern>
      </defs>
      <rect width="240" height="14" fill="url(#chev)" />
    </svg>
  );
}

/* ══════════════════════════════════════ HERO ══════════════════════════════════════ */
function Hero() {
  return (
    <div style={{ position: 'relative', textAlign: 'center', padding: '5.5rem 1rem 3rem', overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background:
            `radial-gradient(circle at 22% 40%, rgba(27,127,90,0.18) 0%, transparent 55%), radial-gradient(circle at 80% 55%, rgba(201,162,39,0.10) 0%, transparent 55%)`,
        }}
      />

      <div
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 16px', borderRadius: 100,
          background: 'rgba(27,127,90,0.12)', border: `1px solid ${C.border}`,
          fontSize: '0.78rem', fontWeight: 500, color: C.muted,
          marginBottom: '1.6rem', letterSpacing: '0.02em',
        }}
      >
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: C.emeraldBright, animation: 'pulse 2s ease-in-out infinite' }} />
        Open Source · MIT Licensed · Memory layer for agentic AI
      </div>

      <h1 style={{ fontSize: 'clamp(2.4rem, 5.4vw, 4.2rem)', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.08, marginBottom: '1.1rem', color: C.text }}>
        Memory Infrastructure<br />for <GradientText>Agentic AI</GradientText>
      </h1>

      <p style={{ fontSize: 'clamp(1rem, 2vw, 1.18rem)', color: C.muted, maxWidth: 660, margin: '0 auto 2.2rem', lineHeight: 1.7 }}>
        Chengeta AI gives intelligent agents a persistent, high-performance memory layer across
        frameworks, workflows, and environments — so they recall what they have already done
        instead of paying to recompute it.
      </p>

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '2.2rem' }}>
        <Link to="/docs/getting-started/quickstart" className="cta-primary"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8, padding: '0.8rem 1.9rem', borderRadius: 100,
            background: GRADIENT, color: '#0A140E', fontWeight: 700, fontSize: '0.94rem', textDecoration: 'none',
            boxShadow: '0 6px 24px rgba(27,127,90,0.32)', transition: 'all 0.25s',
          }}>
          Get Started →
        </Link>
        <Link to="/docs/getting-started/installation" className="cta-secondary"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8, padding: '0.8rem 1.9rem', borderRadius: 100,
            background: 'rgba(27,127,90,0.10)', border: `1px solid ${C.border}`, color: C.text,
            fontWeight: 600, fontSize: '0.94rem', textDecoration: 'none', transition: 'all 0.25s',
          }}>
          View Documentation
        </Link>
        <a href="https://github.com/vigilancetrent/chengeta-ai" className="cta-secondary"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8, padding: '0.8rem 1.9rem', borderRadius: 100,
            background: 'rgba(27,127,90,0.10)', border: `1px solid ${C.border}`, color: C.text,
            fontWeight: 600, fontSize: '0.94rem', textDecoration: 'none', transition: 'all 0.25s',
          }}>
          ★ GitHub
        </a>
      </div>

      <div
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 12, padding: '0.7rem 1.25rem',
          background: C.panelAlt, border: `1px solid ${C.border}`, borderRadius: 10,
          fontFamily: '"JetBrains Mono","Fira Code",monospace', fontSize: '0.82rem', color: '#CDE0D4',
        }}
      >
        <span style={{ color: C.gold, userSelect: 'none' }}>$</span>
        pip install chengeta-ai
      </div>

      <style>{`
        @keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }
        .cta-primary:hover { box-shadow: 0 8px 30px rgba(201,162,39,0.4) !important; transform: translateY(-1px); color: #0A140E !important; }
        .cta-secondary:hover { border-color: ${C.emeraldBright} !important; color: ${C.emeraldBright} !important; transform: translateY(-1px); }
      `}</style>
    </div>
  );
}

/* ══════════════════════════════════════ STATS ══════════════════════════════════════ */
const stats = [
  { number: '8', label: 'Memory Layers' },
  { number: '9', label: 'Storage Backends' },
  { number: '13+', label: 'Framework Adapters' },
  { number: '90%', label: 'Cost Reduction' },
];

function StatsBar() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', gap: '3.5rem', padding: '2rem 1rem', flexWrap: 'wrap', borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}`, background: 'rgba(16,33,26,0.5)' }}>
      {stats.map((s) => (
        <div key={s.label} style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, lineHeight: 1.2, background: GRADIENT, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>{s.number}</div>
          <div style={{ fontSize: '0.74rem', color: C.faint, textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 4, fontWeight: 500 }}>{s.label}</div>
        </div>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════ WHY CHENGETA ══════════════════════════════════════ */
const features = [
  { icon: '∞', title: 'Persistent by Design', desc: 'Memory survives turns, sessions, and restarts. What an agent learns once is preserved — chengeta means to keep safe.', href: '/docs/layers/context', link: 'Context memory' },
  { icon: '◇', title: 'Semantic Recall', desc: 'Returns saved answers for semantically similar queries via cosine similarity, with an adaptive auto-tuning threshold.', href: '/docs/layers/semantic', link: 'Semantic layer' },
  { icon: '⚡', title: 'Microsecond Hits', desc: 'In-memory LRU hits return in microseconds — orders of magnitude faster than an LLM or vector round-trip.', href: '/docs/backends/memory', link: 'Backends' },
  { icon: '◼', title: 'Framework-Agnostic', desc: 'One memory layer across LangChain, LangGraph, CrewAI, AutoGen, Agno, A2A, OpenAI, Anthropic, Gemini and more.', href: '/docs/adapters', link: 'Adapters' },
  { icon: '⬡', title: 'Production Backends', desc: 'In-Memory, Disk, Redis, tiered L1+L2, FAISS, Chroma, Qdrant, Weaviate, Pinecone — pick your scale.', href: '/docs/backends', link: 'Storage' },
  { icon: '⌖', title: 'Observable & Safe', desc: 'Tag-based invalidation, stampede protection, multi-tenant namespacing, Prometheus and OpenTelemetry export.', href: '/docs/core/observability', link: 'Observability' },
];

function FeatureCard({ icon, title, desc, href, link }: typeof features[0]) {
  const [hovered, setHovered] = React.useState(false);
  return (
    <Link to={href} style={{ textDecoration: 'none' }} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}>
      <div style={{
        position: 'relative', padding: '1.6rem', borderRadius: 16,
        border: `1px solid ${hovered ? C.emeraldBright : C.border}`,
        background: hovered ? 'rgba(27,127,90,0.06)' : C.panel,
        transition: 'all 0.3s cubic-bezier(0.4,0,0.2,1)',
        boxShadow: hovered ? '0 0 32px rgba(27,127,90,0.2)' : '0 4px 20px rgba(0,0,0,0.3)',
        transform: hovered ? 'translateY(-4px)' : 'none', height: '100%', overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: GRADIENT, opacity: hovered ? 1 : 0, transition: 'opacity 0.3s' }} />
        <div style={{ fontSize: '1.7rem', marginBottom: '0.7rem', color: C.gold, lineHeight: 1 }}>{icon}</div>
        <div style={{ fontWeight: 700, fontSize: '1.02rem', color: C.text, marginBottom: '0.4rem' }}>{title}</div>
        <p style={{ color: C.muted, fontSize: '0.875rem', lineHeight: 1.6, margin: 0 }}>{desc}</p>
        <div style={{ marginTop: '0.8rem', fontSize: '0.82rem', fontWeight: 600, color: C.emeraldBright }}>{link} →</div>
      </div>
    </Link>
  );
}

function WhyChengeta() {
  return (
    <div style={{ padding: '4rem 1rem', maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center', fontWeight: 800, fontSize: 'clamp(1.6rem, 3vw, 2.2rem)', letterSpacing: '-0.02em', marginBottom: '0.75rem', color: C.text }}>
        Why <GradientText>Chengeta</GradientText>
      </h2>
      <p style={{ textAlign: 'center', color: C.muted, maxWidth: 600, margin: '0 auto 3rem', fontSize: '1rem', lineHeight: 1.6 }}>
        Agentic systems are expensive because they are forgetful. Chengeta AI is the layer that makes them remember.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
        {features.map((f) => <FeatureCard key={f.title} {...f} />)}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════ SUPPORTED FRAMEWORKS ══════════════════════════════════════ */
const frameworks = ['LangChain', 'LangGraph', 'AutoGen', 'CrewAI', 'Agno', 'A2A', 'OpenAI', 'Anthropic', 'Gemini', 'Google ADK', 'LlamaIndex', 'OpenAI Agents', 'Claude Agent'];

function SupportedFrameworks() {
  return (
    <div style={{ padding: '2rem 1rem', textAlign: 'center', maxWidth: 900, margin: '0 auto' }}>
      <h2 style={{ fontWeight: 800, fontSize: 'clamp(1.4rem,2.6vw,1.9rem)', letterSpacing: '-0.02em', marginBottom: '0.6rem', color: C.text }}>
        Supported <GradientText>Frameworks</GradientText>
      </h2>
      <p style={{ color: C.faint, fontSize: '0.85rem', marginBottom: '1.6rem' }}>Drop in anywhere — no call signatures change.</p>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '0.7rem', flexWrap: 'wrap' }}>
        {frameworks.map((fw) => (
          <span key={fw} style={{ padding: '0.4rem 1.05rem', borderRadius: 100, background: 'rgba(27,127,90,0.10)', border: `1px solid ${C.border}`, fontSize: '0.84rem', fontWeight: 500, color: C.muted }}>{fw}</span>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════ MEMORY LAYERS ══════════════════════════════════════ */
const layers = [
  { name: 'ResponseCache', what: 'LLM output by model + messages + params' },
  { name: 'EmbeddingCache', what: 'Vectors by model + text, stored as bytes' },
  { name: 'RetrievalCache', what: 'Documents by query + retriever + top-k' },
  { name: 'ContextCache', what: 'Conversation turns by session + index' },
  { name: 'SemanticCache', what: 'Answers for cosine-similar queries' },
  { name: 'AdaptiveSemanticCache', what: 'Semantic + auto-tuning threshold' },
  { name: 'StreamingResponseCache', what: 'Buffered stream replay as a generator' },
  { name: 'PromptCacheLayer', what: 'Provider cache_control + savings tracking' },
];

function MemoryLayers() {
  return (
    <div style={{ padding: '4rem 1rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center', fontWeight: 800, fontSize: 'clamp(1.6rem,3vw,2.2rem)', letterSpacing: '-0.02em', marginBottom: '0.75rem', color: C.text }}>
        Eight <GradientText>Memory Layers</GradientText>
      </h2>
      <p style={{ textAlign: 'center', color: C.muted, maxWidth: 560, margin: '0 auto 2.5rem', fontSize: '1rem' }}>
        Each layer preserves one kind of artifact, with serialization tuned to its data.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.9rem' }}>
        {layers.map((l, i) => (
          <div key={l.name} style={{ display: 'flex', gap: 12, padding: '1rem 1.1rem', borderRadius: 12, background: C.panel, border: `1px solid ${C.border}` }}>
            <span style={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.8rem', color: C.gold, fontWeight: 700 }}>{String(i + 1).padStart(2, '0')}</span>
            <div>
              <div style={{ fontFamily: '"JetBrains Mono",monospace', fontWeight: 600, fontSize: '0.84rem', color: C.emeraldBright }}>{l.name}</div>
              <div style={{ color: C.muted, fontSize: '0.8rem', marginTop: 3, lineHeight: 1.45 }}>{l.what}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════ PERFORMANCE BENCHMARKS ══════════════════════════════════════ */
const benchmarks = [
  { op: 'In-memory cache hit', cold: '~600 ms (LLM call)', warm: '< 0.1 ms', x: '6,000×' },
  { op: 'Embedding reuse', cold: '~80 ms (embed API)', warm: '< 0.2 ms', x: '400×' },
  { op: 'Retrieval recall', cold: '~22 ms (vector DB)', warm: '< 0.3 ms', x: '70×' },
  { op: 'Semantic match', cold: '~600 ms (LLM call)', warm: '~2 ms', x: '300×' },
];

function Benchmarks() {
  return (
    <div style={{ padding: '4rem 1rem', maxWidth: 900, margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center', fontWeight: 800, fontSize: 'clamp(1.6rem,3vw,2.2rem)', letterSpacing: '-0.02em', marginBottom: '0.75rem', color: C.text }}>
        Performance <GradientText>Benchmarks</GradientText>
      </h2>
      <p style={{ textAlign: 'center', color: C.muted, maxWidth: 560, margin: '0 auto 2.2rem', fontSize: '1rem' }}>
        A warm cache turns network round-trips into local reads. Figures are representative of typical workloads.
      </p>
      <div style={{ borderRadius: 14, overflow: 'hidden', border: `1px solid ${C.border}`, boxShadow: '0 8px 32px rgba(0,0,0,0.4)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {['Operation', 'Cold (miss)', 'Warm (hit)', 'Speed-up'].map((h, i) => (
                <th key={h} style={{ padding: '0.85rem 1.1rem', background: C.panel, color: i === 3 ? C.gold : C.muted, fontWeight: 700, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', textAlign: 'left', borderBottom: `2px solid ${C.border}` }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {benchmarks.map((b, i) => (
              <tr key={b.op} style={{ background: i % 2 === 0 ? C.panelAlt : C.panel }}>
                <td style={{ padding: '0.8rem 1.1rem', color: C.text, fontSize: '0.86rem', fontWeight: 500 }}>{b.op}</td>
                <td style={{ padding: '0.8rem 1.1rem', color: C.muted, fontSize: '0.86rem' }}>{b.cold}</td>
                <td style={{ padding: '0.8rem 1.1rem', color: C.emeraldBright, fontSize: '0.86rem', fontFamily: '"JetBrains Mono",monospace' }}>{b.warm}</td>
                <td style={{ padding: '0.8rem 1.1rem', color: C.gold, fontSize: '0.86rem', fontWeight: 700 }}>{b.x}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════ ARCHITECTURE ══════════════════════════════════════ */
const archStages = [
  { label: 'Framework Adapter', sub: 'LangChain · CrewAI · OpenAI …' },
  { label: 'Middleware', sub: 'wrap any callable' },
  { label: 'Memory Layers', sub: '8 cache layers' },
  { label: 'Backend', sub: 'KV or Vector store' },
];

function Architecture() {
  return (
    <div style={{ padding: '4rem 1rem', maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center', fontWeight: 800, fontSize: 'clamp(1.6rem,3vw,2.2rem)', letterSpacing: '-0.02em', marginBottom: '0.75rem', color: C.text }}>
        <GradientText>Architecture</GradientText>
      </h2>
      <p style={{ textAlign: 'center', color: C.muted, maxWidth: 620, margin: '0 auto 2.5rem', fontSize: '1rem' }}>
        A request flows through adapter and middleware into the memory layers. On a hit, it returns instantly.
        On a miss, the real call runs once, the result is preserved, and every future request is served from memory.
      </p>
      <div style={{ display: 'flex', alignItems: 'stretch', justifyContent: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
        {archStages.map((s, i) => (
          <React.Fragment key={s.label}>
            <div style={{ flex: '1 1 180px', minWidth: 160, padding: '1.2rem 1rem', borderRadius: 12, background: C.panel, border: `1px solid ${C.border}`, textAlign: 'center' }}>
              <div style={{ fontWeight: 700, color: C.text, fontSize: '0.92rem' }}>{s.label}</div>
              <div style={{ color: C.faint, fontSize: '0.76rem', marginTop: 4 }}>{s.sub}</div>
            </div>
            {i < archStages.length - 1 && (
              <div style={{ display: 'flex', alignItems: 'center', color: C.gold, fontSize: '1.2rem', fontWeight: 700 }}>→</div>
            )}
          </React.Fragment>
        ))}
      </div>
      <div style={{ marginTop: '1.4rem', textAlign: 'center', color: C.faint, fontSize: '0.82rem' }}>
        Miss → real API call → <span style={{ color: C.emeraldBright }}>preserve in memory</span> → return
      </div>
    </div>
  );
}

/* ══════════════════════════════════════ COMMUNITY ══════════════════════════════════════ */
const community = [
  { icon: '★', title: 'Star on GitHub', desc: 'Follow development and shape the roadmap.', href: 'https://github.com/vigilancetrent/chengeta-ai' },
  { icon: '✦', title: 'Discussions', desc: 'Ask questions and share patterns.', href: 'https://github.com/vigilancetrent/chengeta-ai/discussions' },
  { icon: '◈', title: 'Contribute', desc: 'Add a backend, adapter, or recipe.', href: 'https://github.com/vigilancetrent/chengeta-ai/blob/main/CONTRIBUTING.md' },
  { icon: '◆', title: 'Read the Docs', desc: 'Guides, cookbook, and API reference.', href: '/docs/getting-started/installation' },
];

function Community() {
  return (
    <div style={{ padding: '4rem 1rem 5rem', maxWidth: 980, margin: '0 auto' }}>
      <ChevronBand />
      <h2 style={{ textAlign: 'center', fontWeight: 800, fontSize: 'clamp(1.6rem,3vw,2.2rem)', letterSpacing: '-0.02em', margin: '2.2rem 0 0.75rem', color: C.text }}>
        Join the <GradientText>Community</GradientText>
      </h2>
      <p style={{ textAlign: 'center', color: C.muted, maxWidth: 560, margin: '0 auto 2.5rem', fontSize: '1rem' }}>
        Chengeta AI is built in the open. Bring your frameworks, your scale, and your ideas.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem' }}>
        {community.map((item) => (
          <CommunityCard key={item.title} {...item} />
        ))}
      </div>
    </div>
  );
}

function CommunityCard({ icon, title, desc, href }: typeof community[0]) {
  const [hovered, setHovered] = React.useState(false);
  const inner = (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'flex-start', height: '100%',
      padding: '1.4rem', borderRadius: 14,
      border: `1px solid ${hovered ? C.emeraldBright : C.border}`,
      background: hovered ? 'rgba(27,127,90,0.06)' : C.panel,
      transition: 'all 0.25s', transform: hovered ? 'translateY(-3px)' : 'none',
    }}>
      <span style={{ fontSize: '1.5rem', marginBottom: '0.6rem', color: C.gold }}>{icon}</span>
      <div style={{ fontWeight: 700, color: C.text, fontSize: '0.95rem', marginBottom: '0.3rem' }}>{title}</div>
      <p style={{ color: C.muted, fontSize: '0.82rem', margin: 0, lineHeight: 1.5 }}>{desc}</p>
    </div>
  );
  const props = { onMouseEnter: () => setHovered(true), onMouseLeave: () => setHovered(false), style: { textDecoration: 'none' } };
  return href.startsWith('http')
    ? <a href={href} {...props}>{inner}</a>
    : <Link to={href} {...props}>{inner}</Link>;
}

/* ══════════════════════════════════════ ROOT ══════════════════════════════════════ */
export default function Home() {
  return (
    <Layout
      title="Memory Infrastructure for Agentic AI"
      description="Chengeta AI gives intelligent agents a persistent, high-performance memory layer across frameworks, workflows, and environments."
    >
      <main style={{ background: C.bg }}>
        <Hero />
        <StatsBar />
        <WhyChengeta />
        <Divider />
        <SupportedFrameworks />
        <Divider />
        <MemoryLayers />
        <Divider />
        <Benchmarks />
        <Divider />
        <Architecture />
        <Community />
      </main>
    </Layout>
  );
}
