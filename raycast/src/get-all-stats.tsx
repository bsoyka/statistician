import { Action, ActionPanel, Color, Icon, List, useNavigation } from "@raycast/api";
import { useEffect, useState } from "react";
import { apiGet, formatDate } from "./api";
import { Stat } from "./types";
import { UpdateStat } from "./update-stat";

export default function GetAllStats() {
  const [stats, setStats] = useState<Stat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { push } = useNavigation();

  async function loadStats() {
    setIsLoading(true);
    try {
      const data = await apiGet<{ items: Stat[] }>("/private/stats");
      setStats(data.items.sort((a, b) => a.label.localeCompare(b.label)));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadStats();
  }, []);

  return (
    <List isLoading={isLoading} searchBarPlaceholder="Search stats…">
      {stats.map((stat) => (
        <List.Item
          key={stat.stat_key}
          title={stat.label}
          subtitle={String(stat.value)}
          accessories={[
            stat.public
              ? { tag: { value: "Public", color: Color.Green } }
              : { tag: { value: "Private", color: Color.SecondaryText } },
            { date: new Date(stat.updated_at), tooltip: `Updated ${formatDate(stat.updated_at)}` },
          ]}
          actions={
            <ActionPanel>
              <Action
                title="Edit Stat"
                icon={Icon.Pencil}
                onAction={() =>
                  push(
                    <UpdateStat
                      statKey={stat.stat_key}
                      initialValues={{
                        value: stat.value,
                        label: stat.label,
                        isPublic: stat.public,
                        funFactTemplate: stat.fun_fact_template ?? "",
                      }}
                      onSuccess={loadStats}
                    />,
                  )
                }
              />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
