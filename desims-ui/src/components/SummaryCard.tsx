
type SummaryCardProps = {
    title: string;
    value: number;
    description: string;
};

function SummaryCard({ title, value, description }: SummaryCardProps) {
    return (
        <section className="card">
            <p className="card-label">{title}</p>
            <p className="card-value">{value}</p>
            <div className="card-footer">{description}</div>
        </section>
    );
}

export default SummaryCard;
