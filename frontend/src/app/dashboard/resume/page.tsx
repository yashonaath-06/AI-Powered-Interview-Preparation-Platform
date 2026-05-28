import { Card, CardDescription, CardTitle } from "@/components/ui/Card";

export default function ResumePage() {
  return (
    <div className="p-6 lg:p-10 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Resume Analyzer</h1>
      <Card>
        <CardTitle>🚧 Coming in Phase 13</CardTitle>
        <CardDescription className="mt-2">
          Upload your PDF resume and we&apos;ll extract skills, match them against your
          target role, and generate AI feedback.
        </CardDescription>
      </Card>
    </div>
  );
}
