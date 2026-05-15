"use client";

import { useQuery } from "@tanstack/react-query";
import { getJob, type Job } from "@/lib/api";

export function useJobStatus(jobId: string, enabled = true) {
  return useQuery<Job>({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
    enabled: enabled && !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed" || status === "expired") {
        return false;
      }
      return 2000;
    },
  });
}
