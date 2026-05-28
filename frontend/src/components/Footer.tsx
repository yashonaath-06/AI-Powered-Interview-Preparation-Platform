export function Footer() {
  return (
    <footer className="py-10 border-t border-slate-100 bg-white">
      <div className="container-tight flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
        <p>© {new Date().getFullYear()} AI Interview Prep — Final-year project.</p>
        <p>Built with Next.js · FastAPI · Whisper · MediaPipe</p>
      </div>
    </footer>
  );
}
