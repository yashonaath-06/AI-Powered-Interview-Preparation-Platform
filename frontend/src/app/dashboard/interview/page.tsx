/**
 * Placeholder. The full Interview Studio (webcam + mic + question flow)
 * is built in Phases 7-10.
 */
import { Card, CardDescription, CardTitle } from "@/components/ui/Card";

export default function InterviewPage() {
  return (
    <div className="p-6 lg:p-10 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Mock Interview Studio</h1>
      <Card>
        <CardTitle>🚧 Coming in Phase 7</CardTitle>
        <CardDescription className="mt-2">
          The AI-powered interview engine, camera + mic capture, and live transcription
          will be wired up in upcoming phases. Right now you can already sign in,
          sign up, and see this dashboard load real data from the backend.
        </CardDescription>
      </Card>
    </div>
  );
}
