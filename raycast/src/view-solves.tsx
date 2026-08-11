import { Action, ActionPanel, Color, Icon, List } from "@raycast/api";
import { useEffect, useState } from "react";
import { apiGet, formatSolveTime } from "./api";
import { Solve, SolveSummary } from "./types";

const EVENT = "333";
const RECENT_COUNT = 50;

export default function ViewSolves() {
  const [solves, setSolves] = useState<Solve[]>([]);
  const [summary, setSummary] = useState<SolveSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const [solvesData, summaryData] = await Promise.all([
          apiGet<{ items: Solve[] }>(`/private/solves?event=${EVENT}`),
          apiGet<SolveSummary>(`/private/solves/summary?event=${EVENT}`),
        ]);
        setSolves(solvesData.items.slice(-RECENT_COUNT).reverse());
        setSummary(summaryData);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <List isLoading={isLoading}>
      {summary && (
        <List.Section title="3x3 Stats">
          <List.Item title="Solve Count" icon={Icon.Hashtag} accessories={[{ text: String(summary.count_total) }]} />
          <List.Item
            title="PR Single"
            icon={Icon.Trophy}
            accessories={[{ text: summary.pr_single_ms !== null ? formatSolveTime(summary.pr_single_ms) : "—" }]}
          />
          <List.Item
            title="Current Ao5"
            icon={Icon.LineChart}
            accessories={[{ text: summary.current_ao5_ms !== null ? formatSolveTime(summary.current_ao5_ms) : "—" }]}
          />
          <List.Item
            title="Current Ao12"
            icon={Icon.LineChart}
            accessories={[
              { text: summary.current_ao12_ms !== null ? formatSolveTime(summary.current_ao12_ms) : "—" },
            ]}
          />
        </List.Section>
      )}
      <List.Section title="Recent Solves">
        {solves.map((solve) => {
          const accessories: List.Item.Accessory[] = [];
          if (solve.penalty) {
            accessories.push({
              tag: { value: solve.penalty, color: solve.penalty === "DNF" ? Color.Red : Color.Orange },
            });
          }
          accessories.push({ text: new Date(solve.timestamp).toLocaleString(), tooltip: solve.timestamp });

          return (
            <List.Item
              key={solve.sk}
              title={formatSolveTime(solve.time_ms)}
              subtitle={solve.source}
              accessories={accessories}
              actions={
                <ActionPanel>
                  <Action.CopyToClipboard title="Copy Scramble" content={solve.scramble} />
                </ActionPanel>
              }
            />
          );
        })}
      </List.Section>
    </List>
  );
}
