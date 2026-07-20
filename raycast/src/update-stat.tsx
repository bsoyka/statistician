import { Action, ActionPanel, Form, LaunchProps, showToast, Toast, useNavigation } from "@raycast/api";
import { useEffect, useState } from "react";
import { apiGet, apiPut } from "./api";
import { Stat } from "./types";

interface UpdateStatFormValues {
  value: string;
  label: string;
  isPublic: boolean;
  funFactTemplate: string;
}

export interface UpdateStatProps {
  statKey?: string;
  initialValues?: {
    value: number;
    label: string;
    isPublic: boolean;
    funFactTemplate: string;
  };
  onSuccess?: () => void;
}

// Reusable form component — also the default export for the standalone command.
export function UpdateStat({ statKey, initialValues, onSuccess }: UpdateStatProps) {
  const { pop } = useNavigation();
  const [isLoading, setIsLoading] = useState(!initialValues && !!statKey);
  const [fetchedStat, setFetchedStat] = useState<Stat | null>(null);

  // Only fetch when we have a key but no pre-filled values (standalone launch with argument).
  useEffect(() => {
    if (statKey && !initialValues) {
      setIsLoading(true);
      apiGet<Stat>(`/private/stats/${statKey}`)
        .then(setFetchedStat)
        .catch(() => undefined)
        .finally(() => setIsLoading(false));
    }
  }, [statKey, initialValues]);

  // Derive the values to prefill the form from whichever source is available.
  const prefill =
    initialValues ??
    (fetchedStat
      ? {
          value: fetchedStat.value,
          label: fetchedStat.label,
          isPublic: fetchedStat.public,
          funFactTemplate: fetchedStat.fun_fact_template ?? "",
        }
      : null);

  async function handleSubmit(values: UpdateStatFormValues) {
    const key = statKey ?? fetchedStat?.stat_key;
    if (!key) {
      await showToast({ style: Toast.Style.Failure, title: "No stat key — enter one above" });
      return;
    }

    const numValue = parseFloat(values.value);
    if (isNaN(numValue)) {
      await showToast({ style: Toast.Style.Failure, title: "Value must be a number" });
      return;
    }

    setIsLoading(true);
    try {
      await apiPut<Stat>(`/private/stats/${key}`, {
        value: numValue,
        label: values.label,
        public: values.isPublic,
        ...(values.funFactTemplate ? { fun_fact_template: values.funFactTemplate } : {}),
      });
      await showToast({ style: Toast.Style.Success, title: "Stat updated" });
      onSuccess?.();
      pop();
    } finally {
      setIsLoading(false);
    }
  }

  // When fetching by key, hold off rendering fields until data arrives so
  // defaultValue is populated on the first (and only) mount of each field.
  if (statKey && !initialValues && !fetchedStat && isLoading) {
    return <Form isLoading actions={<ActionPanel />} />;
  }

  return (
    <Form
      isLoading={isLoading}
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Update Stat" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.TextField
        id="value"
        title="Value"
        placeholder="e.g. 42"
        defaultValue={prefill ? String(prefill.value) : ""}
      />
      <Form.TextField id="label" title="Label" placeholder="e.g. Books Read" defaultValue={prefill?.label ?? ""} />
      <Form.Checkbox id="isPublic" label="Public" defaultValue={prefill?.isPublic ?? false} />
      <Form.TextField
        id="funFactTemplate"
        title="Fun Fact Template"
        placeholder="e.g. I've read {value} books!"
        defaultValue={prefill?.funFactTemplate ?? ""}
      />
    </Form>
  );
}

// Standalone Raycast command entry point.
export default function UpdateStatCommand(props: LaunchProps<{ arguments: { stat_key: string } }>) {
  return <UpdateStat statKey={props.arguments.stat_key} />;
}
