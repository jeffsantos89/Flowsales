// src/dashboards/grafanaDashboardConfig.ts
export const dashboardConfig = {
    title: "Marketing Automation Overview",
    panels: [
      {
        title: "Leads Cadastrados",
        type: "graph",
        targets: [
          {
            expr: "sum(rate(leads_created_total[5m]))",
            legendFormat: "Leads/minuto",
          },
        ],
      },
      {
        title: "Taxa de Conversão",
        type: "gauge",
        targets: [
          {
            expr: "(sum(conversions_total) / sum(leads_created_total)) * 100",
            legendFormat: "Conversão (%)",
          },
        ],
      },
      {
        title: "Previsão de Churn",
        type: "table",
        targets: [
          {
            expr: "sum(rate(churn_predicted_total[5m]))",
            legendFormat: "Churn/minuto",
          },
        ],
      },
    ],
  };
  