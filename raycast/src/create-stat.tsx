import { Action, ActionPanel, Form, showToast, Toast } from "@raycast/api";
import { useState } from "react";
import { apiPut } from "./api";
import { Stat } from "./types";

interface FormValues {
  stat_key: string;
  value: string;
  label: string;
  isPublic: boolean;
  fun_fact_template: string;
}

export default function CreateStat() {
  const [isLoading, setIsLoading] = useState(false);
  const [formKey, setFormKey] = useState(0);

  async function handleSubmit(values: FormValues) {
    const key = values.stat_key.trim();
    if (!key) {
      await showToast({ style: Toast.Style.Failure, title: "Stat key is required" });
      return;
    }

    const value = parseFloat(values.value);
    if (isNaN(value)) {
      await showToast({ style: Toast.Style.Failure, title: "Value must be a number" });
      return;
    }

    setIsLoading(true);
    try {
      await apiPut<Stat>(`/private/stats/${key}`, {
        value,
        label: values.label || key,
        public: values.isPublic,
        ...(values.fun_fact_template ? { fun_fact_template: values.fun_fact_template } : {}),
      });
      await showToast({ style: Toast.Style.Success, title: "Stat created" });
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
          <Action.SubmitForm title="Create Stat" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.TextField id="stat_key" title="Stat Key" placeholder="e.g. fitness.strava.runs_total" />
      <Form.TextField id="value" title="Value" placeholder="e.g. 42" />
      <Form.TextField id="label" title="Label" placeholder="Defaults to stat key if blank" />
      <Form.Checkbox id="isPublic" label="Public" defaultValue={false} />
      <Form.TextField
        id="fun_fact_template"
        title="Fun Fact Template"
        placeholder="Optional, e.g. I've run {value} times!"
      />
    </Form>
  );
}
