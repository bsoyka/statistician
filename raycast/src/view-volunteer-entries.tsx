import { Action, ActionPanel, Color, Detail, Icon, List, useNavigation } from "@raycast/api";
import { useEffect, useState } from "react";
import { apiGet, formatDate, formatMinutes, toISODate } from "./api";
import { VolunteerEntry } from "./types";

function EntryDetail({ entry }: { entry: VolunteerEntry }) {
  const lines: string[] = [
    `# Volunteer Entry — ${entry.date}`,
    ``,
    `**Date:** ${formatDate(entry.date)}`,
    `**Time:** ${formatMinutes(entry.minutes)} (${(entry.minutes / 60).toFixed(1)}h)`,
  ];

  if (entry.organization) lines.push(`**Organization:** ${entry.organization}`);
  if (entry.group_name) lines.push(`**Group Name:** ${entry.group_name}`);
  if (entry.fmsc_meals !== undefined) lines.push(`**FMSC Meals:** ${entry.fmsc_meals}`);
  if (entry.notes) {
    lines.push(``, `**Notes:**`, entry.notes);
  }

  lines.push(``, `*Created: ${formatDate(entry.created_at)}*`, `*Updated: ${formatDate(entry.updated_at)}*`);

  return (
    <Detail
      markdown={lines.join("\n")}
      actions={
        <ActionPanel>
          <Action.CopyToClipboard title="Copy Date" content={entry.date} />
        </ActionPanel>
      }
    />
  );
}

function daysAgo(days: number): Date {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d;
}

const RANGE_OPTIONS: { title: string; value: string; days: number }[] = [
  { title: "Last 30 days", value: "30", days: 30 },
  { title: "Last 90 days", value: "90", days: 90 },
  { title: "Last 180 days", value: "180", days: 180 },
  { title: "Last 365 days", value: "365", days: 365 },
];

export default function ViewVolunteerEntries() {
  const [entries, setEntries] = useState<VolunteerEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { push } = useNavigation();

  async function loadEntries(from: Date, to: Date) {
    setIsLoading(true);
    try {
      const params = `from=${toISODate(from)}&to=${toISODate(to)}`;
      const data = await apiGet<{ items: VolunteerEntry[] }>(`/private/volunteer/entries?${params}`);
      setEntries(data.items);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadEntries(daysAgo(30), new Date());
  }, []);

  function handleRangeChange(value: string) {
    const opt = RANGE_OPTIONS.find((o) => o.value === value);
    if (opt) loadEntries(daysAgo(opt.days), new Date());
  }

  return (
    <List
      isLoading={isLoading}
      searchBarPlaceholder="Search entries…"
      searchBarAccessory={
        <List.Dropdown tooltip="Date Range" storeValue onChange={handleRangeChange}>
          {RANGE_OPTIONS.map((opt) => (
            <List.Dropdown.Item key={opt.value} title={opt.title} value={opt.value} />
          ))}
        </List.Dropdown>
      }
    >
      {entries.map((entry) => {
        const accessories: List.Item.Accessory[] = [];

        if (entry.organization) {
          accessories.push({ tag: { value: entry.organization, color: Color.Blue } });
        }
        if (entry.fmsc_meals !== undefined) {
          accessories.push({ text: `${entry.fmsc_meals} meals`, icon: Icon.Heart });
        }
        // Use a text accessory for date to avoid UTC→local shift on date-only strings.
        accessories.push({ text: formatDate(entry.date), tooltip: entry.date });

        return (
          <List.Item
            key={entry.sk}
            title={formatDate(entry.date)}
            subtitle={formatMinutes(entry.minutes)}
            accessories={accessories}
            actions={
              <ActionPanel>
                <Action title="View Details" icon={Icon.Eye} onAction={() => push(<EntryDetail entry={entry} />)} />
              </ActionPanel>
            }
          />
        );
      })}
    </List>
  );
}
