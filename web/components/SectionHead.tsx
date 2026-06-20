export default function SectionHead({ index, kicker, title, lede }: {
  index: string; kicker: string; title: string; lede?: string;
}) {
  return (
    <div className="s-head">
      <div className="s-index">§{index}</div>
      <div className="s-headmain">
        <span className="s-kicker">{kicker}</span>
        <h2 className="s-title">{title}</h2>
        {lede && <p className="s-lede">{lede}</p>}
      </div>
    </div>
  );
}
