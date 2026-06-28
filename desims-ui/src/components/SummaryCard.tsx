type SummaryCardProps = {
    title: string;
    value: number;
};

function SummaryCard({ title, value }: SummaryCardProps) {
    return (
        <div className="card">
            <h3>{title}</h3>
            <h1>{value}</h1>
        </div>
    );
}

export default SummaryCard;