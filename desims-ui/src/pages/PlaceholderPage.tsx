
type PlaceholderPageProps = {
    title: string;
    description?: string;
};

function PlaceholderPage({
    title,
    description,
}: PlaceholderPageProps) {
    return (
        <main className="dashboard">
            <section className="active-plan-card">
                <h2>{title}</h2>
                <p className="active-plan-description">
                    {description}
                </p>
                <p>This section is not implemented yet.</p>
            </section>
        </main>
    );
}

export default PlaceholderPage;
