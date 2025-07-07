from robusta_krr.core.models.objects import K8sObjectData

from .base import PrometheusMetric, QueryType


class CPULoader(PrometheusMetric):
    """
    A metric loader for loading CPU usage metrics.
    """

    query_type: QueryType = QueryType.QueryRange

    def get_query(self, object: K8sObjectData, duration: str, step: str) -> str:
        print(f"\n\nthis is the CPU loader for {object.kind} {object.name} in namespace {object.namespace} and this is the container: {object.container}\n\n")
        if object.kind == "VirtualMachine":
            pods_selector = f"virt-launcher-{object.name}-.*"
        else:
            pods_selector = "|".join(pod.name for pod in object.pods)
        cluster_label = self.get_prometheus_cluster_label()
        return f"""
            max(
                rate(
                    container_cpu_usage_seconds_total{{
                        namespace="{object.namespace}",
                        pod=~"{pods_selector}",
                        container="{object.container}"
                        {cluster_label}
                    }}[{step}]
                )
            ) by (container, pod, job)
        """


def PercentileCPULoader(percentile: float) -> type[PrometheusMetric]:
    """
    A factory for creating percentile CPU usage metric loaders.
    """

    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")

    class PercentileCPULoader(PrometheusMetric):
        def get_query(self, object: K8sObjectData, duration: str, step: str) -> str:
            if object.kind == "VirtualMachine":
                pods_selector = f"virt-launcher-{object.name}-.*"
            else:
                pods_selector = "|".join(pod.name for pod in object.pods)
            cluster_label = self.get_prometheus_cluster_label()
            return f"""
                quantile_over_time(
                    {round(percentile / 100, 2)},
                    max(
                        rate(
                            container_cpu_usage_seconds_total{{
                                namespace="{object.namespace}",
                                pod=~"{pods_selector}",
                                container="{object.container}"
                                {cluster_label}
                            }}[{step}]
                        )
                    ) by (container, pod, job)
                    [{duration}:{step}]
                )
            """

    return PercentileCPULoader


class CPUAmountLoader(PrometheusMetric):
    """
    A metric loader for loading CPU points count.
    """

    def get_query(self, object: K8sObjectData, duration: str, step: str) -> str:
        if object.kind == "VirtualMachine":
            pods_selector = f"virt-launcher-{object.name}-.*"
        else:
            pods_selector = "|".join(pod.name for pod in object.pods)
        cluster_label = self.get_prometheus_cluster_label()
        return f"""
            count_over_time(
                max(
                    container_cpu_usage_seconds_total{{
                        namespace="{object.namespace}",
                        pod=~"{pods_selector}",
                        container="{object.container}"
                        {cluster_label}
                    }}
                ) by (container, pod, job)
                [{duration}:{step}]
            )
        """
