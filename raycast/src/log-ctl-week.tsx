import { Action, ActionPanel, Form, showToast, Toast } from "@raycast/api";
import { useState } from "react";
import { apiGet, apiPut, toISODate } from "./api";
import { Stat, CtlWeek } from "./types";

interface FormValues {
  week_end_date: Date | null;
  hours: string;
  notes: string;
  people_helped: string;
}

export default function LogCtlWeek() {
  const [isLoading, setIsLoading] = useState(false);
  const [formKey, setFormKey] = useState(0);

  async function handleSubmit(values: FormValues) {
    if (!values.week_end_date) {
      await showToast({ style: Toast.Style.Failure, title: "Week end date is required" });
      return;
    }

    const hours = parseFloat(values.hours);
    if (isNaN(hours) || hours < 0) {
      await showToast({ style: Toast.Style.Failure, title: "Hours must be a non-negative number" });
      return;
    }
    const minutes = Math.round(hours * 60);

    const weekEndDate = toISODate(values.week_end_date);

    const peopleHelped = values.people_helped ? parseInt(values.people_helped, 10) : undefined;
    if (values.people_helped && (isNaN(peopleHelped!) || peopleHelped! < 0)) {
      await showToast({ style: Toast.Style.Failure, title: "People helped must be a non-negative number" });
      return;
    }

    setIsLoading(true);
    try {
      await apiPut<CtlWeek>(`/private/ctl/weeks/${weekEndDate}`, {
        minutes,
        ...(values.notes ? { notes: values.notes } : {}),
      });

      if (peopleHelped !== undefined) {
        const existing = await apiGet<Stat>("/private/stats/volunteering.ctl.people_helped_total");
        await apiPut<Stat>("/private/stats/volunteering.ctl.people_helped_total", {
          value: peopleHelped,
          label: existing.label,
          public: existing.public,
          ...(existing.fun_fact_template ? { fun_fact_template: existing.fun_fact_template } : {}),
        });
      }

      await showToast({ style: Toast.Style.Success, title: "CTL week logged" });
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
          <Action.SubmitForm title="Log CTL Week" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.DatePicker id="week_end_date" title="Week End Date" type={Form.DatePicker.Type.Date} />
      <Form.TextField id="hours" title="Hours" placeholder="e.g. 2" />
      <Form.TextArea id="notes" title="Notes" placeholder="Optional" />
      <Form.TextField id="people_helped" title="People Helped (Total)" placeholder="Optional — updates running total" />
    </Form>
  );
}
