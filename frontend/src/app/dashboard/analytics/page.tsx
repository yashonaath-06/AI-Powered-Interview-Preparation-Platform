import { Card, CardDescription, CardTitle } from "@/components/ui/Card";

export default function AnalyticsPage() {
  return (
    <div className="p-6 lg:p-10 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Performance Analytics</h1>
      <Card>
        <CardTitle>🚧 Coming in Phase 11</CardTitle>
        <CardDescription className="mt-2">
          Charts comparing your scores across sessions, dimension-level trends, and
          AI-generated study recommendations will live here.
        </CardDescription>
      </Card>
    </div>
  );
}
