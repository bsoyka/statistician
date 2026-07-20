import { Action, ActionPanel, Form, showToast, Toast } from "@raycast/api";
import { useState } from "react";
import { apiPost, toISODate } from "./api";
import { VolunteerEntry } from "./types";

interface FormValues {
  date: Date | null;
  hours: string;
  organization: string;
  group_name: string;
  notes: string;
  fmsc_meals: string;
}

export default function LogVolunteerEntry() {
  const [isLoading, setIsLoading] = useState(false);
  // Remount the form to reset all fields after a successful submit.
  const [formKey, setFormKey] = useState(0);

  async function handleSubmit(values: FormValues) {
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
      // Reset form by remounting
      setFormKey((k) => k + 1);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Form
      key={formKey}
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
