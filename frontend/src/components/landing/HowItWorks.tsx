export function HowItWorks() {
  const steps = [
    "Pick company & role",
    "AI asks questions",
    "Camera + mic analyze you",
    "Get a detailed report",
  ];
  return (
    <section id="how" className="py-20">
      <div className="container-tight">
        <h2 className="text-3xl md:text-4xl font-bold text-center">How it works</h2>
        <ol className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          {steps.map((step, i) => (
            <li key={step}>
              <div className="mx-auto w-12 h-12 rounded-full bg-brand-500 text-white font-bold text-lg flex items-center justify-center">
                {i + 1}
              </div>
              <p className="mt-4 font-medium">{step}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
