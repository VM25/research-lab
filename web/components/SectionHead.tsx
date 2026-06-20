/* Section header: a confident title carries the section. No per-section
   eyebrow/number label (templated AI-tell). `kicker`/`index` kept in the
   signature for caller compatibility but intentionally not rendered. */
export default function SectionHead({ title, lede }: {
  index?: string; kicker?: string; title: string; lede?: string;
}) {
  return (
    <div className="s-head">
      <h2 className="s-title">{title}</h2>
      {lede && <p className="s-lede">{lede}</p>}
    </div>
  );
}
