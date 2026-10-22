
type SummaryCardProps = {
    title: string;
    value: number;
};

function SummaryCard({ title, value }: SummaryCardProps) {
    return (
        <section className="card">
            <p className="card-label">{title}</p>

            <p className="card-value">{value}</p>

            <div className="card-footer">
                Department examination overview
            </div>
        </section>
    );
}

export default SummaryCard;
