import {
  Action,
  ActionPanel,
  Color,
  Detail,
  Form,
  Icon,
  Keyboard,
  List,
  showToast,
  Toast,
  useNavigation,
} from "@raycast/api";
import { useEffect, useState } from "react";
import { apiGet, apiPost, formatDate, formatMinutes, toISODate } from "./api";
import { VolunteerEntry } from "./types";

interface LogVolunteerEntryFormValues {
  date: Date | null;
  hours: string;
  organization: string;
  group_name: string;
  notes: string;
  fmsc_meals: string;
}

function LogVolunteerEntry({ onSuccess }: { onSuccess?: () => void }) {
  const [isLoading, setIsLoading] = useState(false);
  const { pop } = useNavigation();

  async function handleSubmit(values: LogVolunteerEntryFormValues) {
    if (!values.date) {
      await showToast({ style: Toast.Style.Failure, title: "Date is required" });
      return;
    }

    const hours = parseFloat(values.hours);
    if (isNaN(hours) || hours <= 0) {
      await showToast({ style: Toast.Style.Failure, title: "Hours must be a positive number" });
      return;
    }
    const minutes = Math.round(hours * 60);

    const fmscMeals = values.fmsc_meals ? parseInt(values.fmsc_meals, 10) : undefined;

    setIsLoading(true);
    try {
      await apiPost<VolunteerEntry>("/private/volunteer/entries", {
        date: toISODate(values.date),
        minutes,
        ...(values.organization ? { organization: values.organization } : {}),
        ...(values.group_name ? { group_name: values.group_name } : {}),
        ...(values.notes ? { notes: values.notes } : {}),
        ...(fmscMeals !== undefined ? { fmsc_meals: fmscMeals } : {}),
      });
      await showToast({ style: Toast.Style.Success, title: "Volunteer entry logged" });
      onSuccess?.();
      pop();
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Form
      isLoading={isLoading}
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Log Entry" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.DatePicker id="date" title="Date" type={Form.DatePicker.Type.Date} />
      <Form.TextField id="hours" title="Hours" placeholder="e.g. 1.5" />
      <Form.TextField id="organization" title="Organization" placeholder="Optional" />
      <Form.TextField id="group_name" title="Group Name" placeholder="Optional" />
      <Form.TextArea id="notes" title="Notes" placeholder="Optional" />
      <Form.TextField id="fmsc_meals" title="FMSC Meals" placeholder="Optional number" />
    </Form>
  );
}

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
  const [rangeDays, setRangeDays] = useState(30);
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
    if (opt) {
      setRangeDays(opt.days);
      loadEntries(daysAgo(opt.days), new Date());
    }
  }

  function reloadCurrentRange() {
    loadEntries(daysAgo(rangeDays), new Date());
  }

  const logEntryAction = (
    <Action
      title="Log Entry"
      icon={Icon.Plus}
      shortcut={Keyboard.Shortcut.Common.New}
      onAction={() => push(<LogVolunteerEntry onSuccess={reloadCurrentRange} />)}
    />
  );

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
      actions={<ActionPanel>{logEntryAction}</ActionPanel>}
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
                {logEntryAction}
              </ActionPanel>
            }
          />
        );
      })}
    </List>
  );
}
